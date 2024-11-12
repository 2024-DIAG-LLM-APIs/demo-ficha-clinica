from openai import OpenAI
from pydantic import BaseModel


class Paciente(BaseModel):
    nombre: str
    fecha_nacimiento: str
    direccion: str
    sintomas: str


class Antecedentes(BaseModel):
    enfermedades_previas: str
    alergias: str


class Atencion(BaseModel):
    sintomas: str
    paciente: Paciente
    antecedentes: Antecedentes


class Razon(BaseModel):
    texto: str


class BooleanResponse(BaseModel):
    isValid: bool
    razon: Razon
    atencion: Atencion


client = OpenAI()

isValid = False
current_data = False
info = None
while not isValid:
    data = input("Ingrese los datos del paciente: ")
    messages = []
    messages.append({
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": """
            Debes verificar que se proporcionen todos los siguientes parámetros: nombre del paciente, fecha de nacimiento, 
            dirección, enfermedades previas, alergias, y síntomas.

            La información que se proporcione debe incluir solo lo previamente especificado 
            (nombre del paciente, fecha de nacimiento, dirección, enfermedades previas, alergias, y síntomas).
            Indicame que datos faltan.
            
            Extrae toda la información y agregala a los datos actuales del paciente.
            """
            }
        ]
    })
    if current_data:
        messages.append({
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": current_data
                }
            ]
        })
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": data
            }
        ]
    })
    validacion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format=BooleanResponse
    )

    current_data = validacion.choices[0].message.content
    info = validacion.choices[0].message.parsed
    if info.atencion.paciente.nombre == "":
        print("Falta el nombre del paciente")
    isValid = validacion.choices[0].message.parsed.isValid
    print(current_data)
    print("Tokens: ", validacion.usage)
    if not isValid:
        print(validacion.choices[0].message.parsed.razon.texto)

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
