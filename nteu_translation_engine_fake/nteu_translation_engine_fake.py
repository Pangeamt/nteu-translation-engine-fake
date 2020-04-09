from aiohttp import web
import signal
import asyncio
import logging
import traceback
import os


class MyTranslationEngine(web.Application):
    def __init__(self):
        super().__init__()

    @staticmethod
    def run():

        # Create server
        server = MyTranslationEngine()
        server.router.add_post(
            "/mytranslation", server.my_translation_handler
        )
        web.run_app(
            server,
            host="0.0.0.0",
            port=5019,
            handle_signals=False
        )
        return server

    async def my_translation_handler(self, request) -> web.Response:
        try:
            data = await request.json()
            texts = data["texts"]
            translations = []

            for text in texts:
                command = text.split()

                if len(command) == 2 and "wait" == command[0]:
                    await asyncio.sleep(int(command[1]))
                elif len(command) == 1 and "error" == command[0]:
                    raise Exception("Error keyword given.")
                elif len(command) == 1 and "shutdown" == command[0]:
                    pid = os.getpid()
                    os.kill(pid, signal.SIGINT)

                translations.append({
                    "my_text": text,
                    "my_translation": text.upper()
                })

            return web.json_response({
                    "my_translations": translations
            })

        except Exception:
            tb = traceback.format_exc()
            tb_str = str(tb)
            logging.error('Error: %s', tb_str)
            return web.Response(text=tb_str, status=500)
