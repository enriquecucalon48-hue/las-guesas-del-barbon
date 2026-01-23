import os
import asyncio
from dotenv import load_dotenv

import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# =========================
# CARGAR .env
# =========================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = int(os.getenv("GRUPO_ID", "0"))

URL_GUARDAR_CHAT = os.getenv(
    "URL_GUARDAR_CHAT",
    "https://las-guesas-del-barbon.onrender.com/bot/guardar-chat/"
)

URL_CONFIRMAR_PEDIDO = os.getenv(
    "URL_CONFIRMAR_PEDIDO",
    "https://las-guesas-del-barbon.onrender.com/bot/confirmar/"
)

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN no definido")

# =========================
# BOT
# =========================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# =========================
# ESTADOS
# =========================

class PedidoState(StatesGroup):
    esperando_direccion = State()
    esperando_comprobante = State()
    esperando_confirmacion = State()

# =========================
# /start
# =========================

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    texto = message.text or ""

    if "pedido_" in texto:
        pedido_id = texto.split("pedido_")[-1]

        # 🔐 Guardar chat_id en Django
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{URL_GUARDAR_CHAT}{pedido_id}/",
                json={"chat_id": message.chat.id}
            )

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

# =========================
# DIRECCIÓN
# =========================

@dp.message(StateFilter(PedidoState.esperando_direccion))
async def recibir_direccion(message: types.Message, state: FSMContext):
    await state.update_data(direccion=message.text)

    await message.answer(
        "💳 *Pago por transferencia*\n\n"
        "*Banco:* Banco Guayaquil\n"
        "*Nombre:* Carlos Valdivieso\n"
        "*Cuenta:* 40041219\n\n"
        "📸 *Envía la foto del comprobante*",
        parse_mode="Markdown"
    )

    await state.set_state(PedidoState.esperando_comprobante)

# =========================
# COMPROBANTE
# =========================

@dp.message(StateFilter(PedidoState.esperando_comprobante), F.photo)
async def recibir_comprobante(message: types.Message, state: FSMContext):
    data = await state.get_data()

    pedido_id = data["pedido_id"]
    direccion = data["direccion"]

    await bot.send_photo(
        chat_id=GRUPO_ID,
        photo=message.photo[-1].file_id,
        caption=(
            "🧾 *COMPROBANTE DE PAGO*\n\n"
            f"Pedido ID: {pedido_id}\n"
            f"Dirección: {direccion}"
        ),
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
        "✅ Comprobante recibido",
        reply_markup=teclado
    )

    await state.set_state(PedidoState.esperando_confirmacion)

# =========================
# CONFIRMAR PEDIDO
# =========================

@dp.callback_query(F.data == "confirmar_pedido")
async def confirmar_pedido(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pedido_id = data["pedido_id"]

    async with aiohttp.ClientSession() as session:
        await session.get(f"{URL_CONFIRMAR_PEDIDO}{pedido_id}/")

    await callback.message.answer(
        "🎉 *Pedido confirmado*\n🟡 En preparación",
        parse_mode="Markdown"
    )

    await state.clear()
    await callback.answer()

# =========================
# MAIN
# =========================

async def main():
    print("🤖 Bot iniciado")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

