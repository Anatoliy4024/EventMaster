import asyncio
from bot.admin_bot.main import run_bot1  # Админ-бот
from bot.picnic_bot.main import run_bot2  # Пикник-бот

async def main():
    # Запускаем оба бота одновременно
    task1 = asyncio.create_task(run_bot1())
    task2 = asyncio.create_task(run_bot2())

    # Ожидание завершения обоих ботов
    await asyncio.gather(task1, task2)

if __name__ == '__main__':
    # Проверяем, существует ли активный цикл событий
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Запускаем основной цикл
    loop.run_until_complete(main())
