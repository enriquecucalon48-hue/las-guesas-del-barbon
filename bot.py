
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ================= CONFIGURACIÓN =================

BOT_TOKEN = "8297994355:AAGeA6LDEOvKimbM8Ktr0R9wRpmvHwVe53M"
GRUPO_ID = -5087703492   # ← TU ID DE GRUPO (ya dijiste que lo tienes)

# ================= BOT =================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================= ESTADOS =================

class PedidoState(StatesGroup):
    esperando_direccion = State()
    esperando_comprobante = State()
    esperando_confirmacion = State()

# ================= START =================

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    texto = message.text or ""

    # Si viene desde la web
    if "pedido_" in texto:
        pedido_id = texto.split("pedido_")[-1]

        await state.set_state(PedidoState.esperando_direccion)
        await state.update_data(pedido_id=pedido_id)

        await message.answer(
            "🍔 *Pedido recibido*\n\n"
            f"🧾 *Pedido ID:* {pedido_id}\n\n"
            "📍 *Escribe tu dirección completa*",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "👋 Bienvenido a *Las Guesas del Barbón*\n\n"
            "🍔 Para hacer un pedido entra primero a nuestra web.",
            parse_mode="Markdown"
        )

# ================= DIRECCIÓN =================

@dp.message(StateFilter(PedidoState.esperando_direccion))
async def recibir_direccion(message: types.Message, state: FSMContext):
    await state.update_data(direccion=message.text)

    await message.answer(
        "💳 *Pago por transferencia*\n\n"
        "*Banco:* Banco Guayaquil\n"
        "*Nombre:* Carlos Valdivieso\n"
        "*Tipo:* Cuenta de ahorros\n"
        "*Cuenta:* 40041219\n"
        "*C.I.:* 0930296470\n\n"
        "📸 *Envía la foto del comprobante*",
        parse_mode="Markdown"
    )

    await state.set_state(PedidoState.esperando_comprobante)

# ================= COMPROBANTE =================

@dp.message(StateFilter(PedidoState.esperando_comprobante), F.photo)
async def recibir_comprobante(message: types.Message, state: FSMContext):
    data = await state.get_data()

    pedido_id = data.get("pedido_id")
    direccion = data.get("direccion")

    caption = (
        "🧾 *COMPROBANTE DE PAGO*\n\n"
        f"🧾 Pedido ID: {pedido_id}\n"
        f"📍 Dirección: {direccion}\n"
        f"👤 Cliente: {message.from_user.full_name}"
    )

    # Enviar foto al grupo
    await bot.send_photo(
        chat_id=GRUPO_ID,
        photo=message.photo[-1].file_id,
        caption=caption,
        parse_mode="Markdown"
    )

    teclado = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(
                text="✅ Confirmar pedido",
                callback_data="confirmar_pedido"
            )]
        ]
    )

    await message.answer(
        "✅ *Comprobante recibido*\n\n"
        "Pulsa el botón para confirmar tu pedido.",
        reply_markup=teclado,
        parse_mode="Markdown"
    )

    await state.set_state(PedidoState.esperando_confirmacion)

# ================= CONFIRMAR =================

@dp.callback_query(F.data == "confirmar_pedido")
async def confirmar_pedido(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.message.answer(
        "🎉 *Pedido confirmado*\n"
        "🟡 En preparación\n\n"
        "🙏 Gracias por tu compra",
        parse_mode="Markdown"
    )

    await bot.send_message(
        chat_id=GRUPO_ID,
        text=(
            "🍔 *PEDIDO CONFIRMADO*\n\n"
            f"🧾 Pedido ID: {data.get('pedido_id')}\n"
            f"📍 Dirección: {data.get('direccion')}"
        ),
        parse_mode="Markdown"
    )

    await state.clear()
    await callback.answer()

# ================= MAIN =================

async def main():
    print("🤖 Bot iniciado correctamente")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

