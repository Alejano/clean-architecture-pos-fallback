package com.fintech.embedded.pos.domain.statemachine

/**
 * Máquina de Estados Determinista para Contingencia EMV Fallback
 * Autor: Alejandro Barragán Jasso
 * Tema 4: Clean Architecture y Corrutinas Resilientes en Lectores POS
 */

// 1. Estados Inmutables del Flujo de Pago
sealed class PaymentState {
    object Idle : PaymentState()
    object WaitingForCard : PaymentState()
    data class ReadingChip(val attempt: Int) : PaymentState()
    data class FallbackToMagstripe(val reason: String) : PaymentState()
    object ReadingMagstripe : PaymentState()
    object RequestingPin : PaymentState()
    data class AuthorizingOnline(val emvTlvData: String) : PaymentState()
    data class Success(val authCode: String, val lastFour: String) : PaymentState()
    data class Failed(val errorCode: String, val message: String) : PaymentState()
}

// 2. Eventos del Hardware y del Usuario
sealed class PaymentEvent {
    object StartPayment : PaymentEvent()
    object CardInserted : PaymentEvent()
    data class ChipReadFailed(val technicalError: String) : PaymentEvent()
    data class ChipReadSuccess(val tlvPayload: String) : PaymentEvent()
    data class CardSwiped(val track2: String) : PaymentEvent()
    data class PinEntered(val pinBlock: String) : PaymentEvent()
    object CardRemovedPrematurely : PaymentEvent()
    object CancelRequested : PaymentEvent()
}

// 3. Orquestador de la Máquina de Estados (State Machine)
class PaymentStateMachine(
    private val onStateChanged: (PaymentState) -> Unit
) {
    private var currentState: PaymentState = PaymentState.Idle
    private var chipFailureCount: Int = 0
    private val MAX_CHIP_ATTEMPTS = 3

    fun processEvent(event: PaymentEvent) {
        val nextState = when (val state = currentState) {
            is PaymentState.Idle -> when (event) {
                is PaymentEvent.StartPayment -> {
                    chipFailureCount = 0
                    PaymentState.WaitingForCard
                }
                else -> state
            }

            is PaymentState.WaitingForCard -> when (event) {
                is PaymentEvent.CardInserted -> {
                    chipFailureCount++
                    PaymentState.ReadingChip(attempt = chipFailureCount)
                }
                is PaymentEvent.CancelRequested -> PaymentState.Idle
                else -> state
            }

            is PaymentState.ReadingChip -> when (event) {
                is PaymentEvent.ChipReadSuccess -> {
                    PaymentState.AuthorizingOnline(event.tlvPayload)
                }
                is PaymentEvent.ChipReadFailed -> {
                    if (chipFailureCount >= MAX_CHIP_ATTEMPTS) {
                        PaymentState.FallbackToMagstripe("Falla consecutiva de chip ($chipFailureCount intentos). Deslice la tarjeta.")
                    } else {
                        PaymentState.WaitingForCard // Solicita reinsertar
                    }
                }
                is PaymentEvent.CardRemovedPrematurely -> {
                    PaymentState.Failed("ERR_CARD_PULLED", "Tarjeta retirada antes de tiempo.")
                }
                else -> state
            }

            is PaymentState.FallbackToMagstripe -> when (event) {
                is PaymentEvent.CardSwiped -> {
                    PaymentState.AuthorizingOnline("FALLBACK_MAGSTRIPE_${event.track2}")
                }
                is PaymentEvent.CancelRequested -> PaymentState.Idle
                else -> state
            }

            else -> state
        }

        if (nextState != currentState) {
            currentState = nextState
            onStateChanged(currentState)
        }
    }
}
