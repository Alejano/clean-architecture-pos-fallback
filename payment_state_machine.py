"""
payment_state_machine.py
Implementación de Referencia Ejecutable: Máquina de Estados para Contingencia Chip Fallback
Autor: Alejandro Barragán Jasso
Tema 4: Clean Architecture y Máquinas de Estado en Lectores de Tarjetas
"""

from enum import Enum, auto
from typing import Optional, List, Callable

class StateType(Enum):
    IDLE = auto()
    WAITING_FOR_CARD = auto()
    READING_CHIP = auto()
    FALLBACK_MAGSTRIPE = auto()
    READING_MAGSTRIPE = auto()
    REQUESTING_PIN = auto()
    AUTHORIZING_ONLINE = auto()
    SUCCESS = auto()
    FAILED = auto()

class CardPaymentFlow:
    """Implementa el patrón de máquina de estados para cobros resilientes con fallback."""

    def __init__(self, logger: Optional[Callable[[str], None]] = None):
        self.state = StateType.IDLE
        self.chip_attempts = 0
        self.max_chip_attempts = 3
        self.history: List[str] = []
        self.logger = logger or print

    def transition(self, next_state: StateType, note: str = ""):
        old_name = self.state.name
        self.state = next_state
        msg = f"  [TRANSICIÓN] {old_name} ---> {next_state.name} {f'({note})' if note else ''}"
        self.history.append(msg)
        self.logger(msg)

    def start_transaction(self, amount: float):
        self.chip_attempts = 0
        self.transition(StateType.WAITING_FOR_CARD, f"Monto: ${amount:.2f}")

    def on_card_inserted(self):
        if self.state not in (StateType.WAITING_FOR_CARD,):
            self.logger("  [IGNORADO] Inserción de tarjeta no esperada en este estado.")
            return
        self.chip_attempts += 1
        self.transition(StateType.READING_CHIP, f"Intento #{self.chip_attempts}")

    def on_chip_read_failed(self, error: str):
        if self.state != StateType.READING_CHIP:
            return
        self.logger(f"  [ERROR HARDWARE] Lectura física de chip fallida: {error}")
        
        if self.chip_attempts >= self.max_chip_attempts:
            self.transition(StateType.FALLBACK_MAGSTRIPE, "3 intentos fallidos de chip -> MODO CONTINGENCIA")
        else:
            self.transition(StateType.WAITING_FOR_CARD, "Reintentar inserción de chip")

    def on_card_swiped(self, track2_masked: str):
        if self.state != StateType.FALLBACK_MAGSTRIPE:
            self.logger("  [RECHAZO] Banda magnética no permitida sin agotar intentos de chip (Anti-Fraude).")
            return
        self.transition(StateType.AUTHORIZING_ONLINE, f"Track2: {track2_masked} (Modo Fallback)")

    def on_host_response(self, approved: bool, auth_code: str = ""):
        if self.state != StateType.AUTHORIZING_ONLINE:
            return
        if approved:
            self.transition(StateType.SUCCESS, f"Aprobado! Auth: {auth_code}")
        else:
            self.transition(StateType.FAILED, "Rechazado por el banco emisor")


def run_demo():
    print("=" * 70)
    print("DEMOSTRACIÓN: MÁQUINA DE ESTADOS DETERMINISTA & EMV FALLBACK")
    print("Autor: Alejandro Barragán Jasso")
    print("=" * 70)

    flow = CardPaymentFlow()

    print("\n1. Iniciando transacción de $850.00 MXN:")
    flow.start_transaction(850.00)

    print("\n2. Intento 1: Tarjeta con chip dañado/sucio:")
    flow.on_card_inserted()
    flow.on_chip_read_failed("MUTE_CHIP_COMMUNICATION_ERROR")

    print("\n3. Intento 2: Segundo intento de chip:")
    flow.on_card_inserted()
    flow.on_chip_read_failed("PARITY_CHECK_FAILED")

    print("\n4. Intento 3: Tercer intento de chip (disparador de Fallback):")
    flow.on_card_inserted()
    flow.on_chip_read_failed("ATR_TIMEOUT")

    print("\n5. Simulando deslizamiento por banda magnética (Contingencia permitida):")
    flow.on_card_swiped("411111******1111=2812")

    print("\n6. Respuesta del Host Bancario:")
    flow.on_host_response(approved=True, auth_code="AUTH98231")

    print(f"\n Estado Final de la Máquina: {flow.state.name}")
    print("\n Demostración de Tema 4 finalizada con éxito.")


if __name__ == "__main__":
    run_demo()
