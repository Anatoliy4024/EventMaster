import asyncio
from bot.admin_bot.main import run_bot1
from bot.picnic_bot.main import run_bot2

async def main():
    # Запуск обоих ботов одновременно
    task1 = asyncio.create_task(run_bot1())
    task2 = asyncio.create_task(run_bot2())

    # Ожидание завершения задач
    await asyncio.gather(task1, task2)

if __name__ == '__main__':
    asyncio.run(main())
