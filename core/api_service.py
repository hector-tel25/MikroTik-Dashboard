"""
core/api_service.py — Capa de servicio que encapsula todas las
llamadas a la API de RouterOS.  No contiene lógica de UI.
"""

from librouteros import connect
from librouteros.exceptions import TrapError, LibRouterosError


class RouterAPI:
    """Wrapper de alto nivel sobre librouteros."""

    def __init__(self):
        self._api = None

    # ── Conexión ──────────────────────────────────────────────

    def connect(self, host: str, username: str,
                password: str, port: int = 8728):
        """Abre la conexión con el router. Lanza excepción si falla."""
        self._api = connect(
            host=host, username=username,
            password=password, port=port,
        )

    def close(self):
        if self._api:
            try:
                self._api.close()
            except Exception:
                pass
            self._api = None

    @property
    def connected(self) -> bool:
        return self._api is not None

    def _require_connection(self):
        if not self._api:
            raise RuntimeError("No hay conexión activa con el router.")

    # ── Interfaces ────────────────────────────────────────────

    def get_interfaces(self) -> list[dict]:
        self._require_connection()
        return list(self._api.path("interface").select())

    def disable_interface(self, iface_id: str):
        self._require_connection()
        self._api.path("interface").disable(id=iface_id)

    def enable_interface(self, iface_id: str):
        self._require_connection()
        self._api.path("interface").enable(id=iface_id)

    def restart_interface(self, iface_id: str):
        """Deshabilita y vuelve a habilitar la interfaz."""
        self.disable_interface(iface_id)
        self.enable_interface(iface_id)

    # ── Direcciones IP ────────────────────────────────────────

    def get_ip_addresses(self) -> list[dict]:
        self._require_connection()
        return list(self._api.path("ip", "address").select())

    def set_interface_ip(self, iface_name: str, ip_cidr: str):
        """Elimina las IPs existentes de la interfaz y asigna la nueva."""
        self._require_connection()
        for addr in self.get_ip_addresses():
            if addr.get("interface") == iface_name:
                self._api.path("ip", "address").remove(addr[".id"])
        self._api.path("ip", "address").add(
            address=ip_cidr, interface=iface_name,
        )

    # ── Usuarios ──────────────────────────────────────────────

    def get_users(self) -> list[dict]:
        self._require_connection()
        return list(self._api.path("user").select())

    def create_user(self, username: str, password: str, group: str):
        self._require_connection()
        self._api.path("user").add(
            name=username, password=password, group=group,
        )

    def delete_user(self, user_id: str):
        self._require_connection()
        self._api.path("user").remove(user_id)

    # ── Monitoreo de tráfico ──────────────────────────────────

    def get_traffic_snapshot(self) -> dict[str, dict]:
        """
        Devuelve un dict { nombre_interfaz: { rx: Mbps, tx: Mbps } }
        para todas las interfaces activas.
        """
        self._require_connection()
        ifaces = self.get_interfaces()
        traffic = {}
        for iface in ifaces:
            name = iface["name"]
            try:
                gen   = self._api("/interface/monitor-traffic",
                                  interface=name, once=True)
                stats = next(gen)
                traffic[name] = {
                    "rx": stats.get("rx-bits-per-second", 0) / 1_000_000,
                    "tx": stats.get("tx-bits-per-second", 0) / 1_000_000,
                }
            except StopIteration:
                traffic[name] = {"rx": 0.0, "tx": 0.0}
        return traffic
