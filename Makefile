# Instala las dependencias
install: requirements.txt
	pipenv install --three
	pipenv run pip3 install -r requirements.txt
# Ejecuta los tests
test:
