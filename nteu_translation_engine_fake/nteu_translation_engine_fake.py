from aiohttp import web
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
            port=config["translationEngineServer"]["port"]
        )
        return server

    async def my_translation_handler(self, request) -> web.Response:
        try:
            data = await request.json()
            texts = data["texts"]
            translations = []

            for text in texts:
                translations.append({
                    "my_text": text,
                    "my_translation": text.upper()
                })

            return web.json_response({
                    "my_translations": translations
            })

        except Exception as e:
            tb = traceback.format_exc()
            tb_str = str(tb)
            logging.error('Error: %s', tb_str)
            return web.Response(text=tb_str, status=500)

    def get_config(self):
        return self._config
