import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Cargar el archivo de chat exportado
file_path = 'chat_responsables.txt'
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Expresión regular para capturar fecha, hora, usuario y mensaje
pattern = r'(\d+/\d+/\d+, \d+:\d+) - ([^:]+): (.+)'

data = []
for line in lines:
    match = re.match(pattern, line)
    if match:
        date_time, user, message = match.groups()
        data.append([date_time, user, message])

# Crear un DataFrame para análisis
df = pd.DataFrame(data, columns=['DateTime', 'User', 'Message'])

# Convertir la columna DateTime en un formato de fecha/hora
df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d/%m/%y, %H:%M')

# Estadísticas básicas: mensajes por usuario
messages_per_user = df['User'].value_counts()

print("Mensajes por usuario:\n", messages_per_user)

# Visualización: Gráfico de barras de mensajes por usuario
messages_per_user.plot(kind='bar')
plt.title('Mensajes por usuario')
plt.xlabel('Usuario')
plt.ylabel('Cantidad de mensajes')
plt.show()

# Crear una nube de palabras para analizar las palabras más utilizadas
all_messages = ' '.join(df['Message'].tolist())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_messages)

# Mostrar la nube de palabras
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
