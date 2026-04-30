import abc
import base64
import uuid

from commons import logs

_LOGGER = logs.get_logger()


class SaveImageError(Exception):
    ...


class AbstractImageAdapter(abc.ABC):
    @abc.abstractmethod
    def save_image(self, image_in_base_64: str) -> str:
        raise NotImplementedError

    @staticmethod
    def generate_random_image_name() -> uuid.UUID:
        return uuid.uuid4()


class LocalImageAdapter(AbstractImageAdapter):
    _DEFAULT_ROUTE = "/static"

    def save_image(self, image_in_base_64: str) -> str:
        image_route = f"{self._DEFAULT_ROUTE}/{self.generate_random_image_name()}.png"
        try:
            # image = Image.open(io.BytesIO(base64.b64decode(image_in_base_64)))
            # image.save(f".{image_route}", optimize=True, quality=75)
            with open(f".{image_route}", "wb") as file:
                file.write(base64.b64decode(image_in_base_64))
            return image_route
        except Exception as e:
            _LOGGER.error(str(e))
            raise SaveImageError()
