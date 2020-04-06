from aiohttp import web
import signal
import asyncio
import logging
import traceback
import yaml
import sys
import os


class MyTranslationEngine(web.Application):
    def __init__(self, config):
        self._config = config
        super().__init__()

    @staticmethod
    def run():
        # Load config
        os.chdir(
            os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
        )
        with open('nteu_adapter_config.yml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        # Create server
        server = MyTranslationEngine(config)
        server.router.add_post(
            "/mytranslation", server.my_translation_handler
        )
        web.run_app(
            server,
            host=config["translationEngineServer"]["host"],
            port=config["translationEngineServer"]["port"],
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

    def get_config(self):
        return self._config
