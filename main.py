from openai import OpenAI
from pydantic import BaseModel


class Razon(BaseModel):
    texto: str


class BooleanResponse(BaseModel):
    isValid: bool
    razon: Razon


client = OpenAI()

data = input("Ingrese los datos del paciente: ")

validacion = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {
          "role": "system",
          "content": [
              {
                  "type": "text",
                  "text": """
                  Debes verificar que se proporcionen todos los siguientes parámetros: nombre del paciente, fecha de nacimiento, 
                  dirección, enfermedades previas, alergias, y síntomas. Responde con "Sí" si todos los parámetros están presentes,
                  o "No" si falta alguno de ellos.

                  La información que se proporcione debe incluir solo lo previamente especificado 
                  (nombre del paciente, fecha de nacimiento, dirección, enfermedades previas, alergias, y síntomas).
                  Indicame que datos faltan.
                  """
              }
          ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": data
                }
            ]
        },
    ],
    temperature=0,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format=BooleanResponse
)

isValid = validacion.choices[0].message.parsed.isValid
print(validacion.choices[0].message.parsed.razon.texto)
print(isValid)

print("Tokens: ", validacion.usage)
if isValid:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": """
                        Eres un asistente especialista en escribir fichas clinicas. Debes utilizar solo la información entregada y no inventar antecedentes.
                        La información a entregar sera: nombre del paciente, fecha de nacimiento, dirección; en antecedentes entregaremos enfermedades previas y alergias,
                        Además se entregará los sintomas. Con esto debes proponer un tratamiento

dentro de la ficha incluye el sexo segun el nombre
                        """
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": data
                    }
                ]
            },
        ],
        temperature=1.0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "text"
        }
    )

    print(response.choices[0].message.content)
    print("Tokens: ", response.usage)
else:
    print("Faltan datos")
