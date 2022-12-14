from xml.sax.handler import feature_namespaces
from xml.sax import make_parser
from pathlib import Path
from xml.sax.handler import ContentHandler
from pysd.translators.structures import abstract_expressions, abstract_model
from pysd.builders.python.python_model_builder import ModelBuilder


class PysdElementsHandler(ContentHandler):
    def __init__(self):
        super().__init__()
        self.elements = []

    def startElementNS(self, name, qname, attrs):
        if name[1] == "UserObject":
            print(f"Name: {attrs.getValueByQName('Name')=}")
            print(f"Doc: {attrs.getValueByQName('Doc')=}")
            print(f"Units: {attrs.getValueByQName('Units')=}")
            print(f"_equation: {attrs.getValueByQName('_equation')=}")
            print(f"_pysd_type: {attrs.getValueByQName('_pysd_type')=}")


parser = make_parser()
parser.setFeature(feature_namespaces, True)
elements_handler = PysdElementsHandler()
parser.setContentHandler(elements_handler)

file_path = Path("teacup.drawio.xml")
parser.parse(file_path)


model = abstract_model.AbstractModel(
    file_path,
    sections=(
        abstract_model.AbstractSection(
            name="__main__",
            path=file_path.with_suffix(".py"),
            type="main",
            params=[],
            returns=[],
            subscripts=[],
            elements=elements_handler.elements,
            split=False,
            views_dict=None,
        ),
    ),
)

ModelBuilder(model).build_model()
