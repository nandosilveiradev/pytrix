import sys

class PytrixValidator:
    def __init__(self, px_path):
        self.px_path = px_path
        self.px_root = None

    def pytrix_executar_validacao(self):
        import xml.etree.ElementTree as ET
        try:
            px_tree = ET.parse(self.px_path)
            self.px_root = px_tree.getroot()
            return True
        except Exception: return False

    def pytrix_finalizar(self):
        px_data = self.px_root
        self.px_root = None # Mata referência
        return px_data
