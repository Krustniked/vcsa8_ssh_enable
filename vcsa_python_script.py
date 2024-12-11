import requests
import json

# VCSA
vcenter_ip = 'Введите ip или имя DNS'
username = 'учетная запись типа administrator@vsphere.local'
password = 'пароль от учетной записи'

# URL для получения сессии
session_url = f"https://{vcenter_ip}/rest/com/vmware/cis/session"

# Выполнение POST-запроса для получения токена
try:
    response = requests.post(session_url, auth=(username, password), verify=False)
    response.raise_for_status()  # Проверка на ошибки HTTP

    # Извлечение токена из ответа
    token = response.json().get('value')

    if token is None:
        print("Ошибка при получении токена.")
        exit(1)
    else:
        print(f"Токен аутентификации получен: {token}")

except requests.exceptions.RequestException as e:
    print(f"Ошибка при получении токена: {e}")
    exit(1)

# Шапка для request
headers = {
    "vmware-api-session-id": token,
    "Content-Type": "application/json"
}
# json 
data = {
    "enabled": True
}


# Запрос для включения web-ui
try:
    response_web = requests.post(f"https://{vcenter_ip}/api/vcenter/services/vsphere-ui?action=start", headers=headers, verify=False)
    response_status_web = requests.get(f"https://{vcenter_ip}/api/vcenter/services/vsphere-ui", headers=headers, verify=False)
    # Проверка статуса ответа
    current_status = response_status_web.json().get('state')
    if current_status == 'STARTED':
        print("Доступ к веб-клиенту VCSA успешно разрешен.")
    else:
        print(f"Ошибка при разрешении доступа к веб-клиенту VCSA: {response_web.text}")

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")

# Запрос вклюсения локального входа
try:
    # Выполняем PUT запрос
    response_local = requests.put(f"https://{vcenter_ip}/rest/appliance/access/consolecli", 
                            headers=headers, 
                            json=data, 
                            verify=False)  

    # Проверяем статус ответа
    if response_local.status_code == 200:
        print("Локальный вход с консоли успешно разрешен.")
    else:
        print(f"Ошибка при разрешении локального входа с консоли: {response_local.status_code} - {response_local.text}")

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")

# ssh
try:

    response_ssh = requests.put(f"https://{vcenter_ip}/rest/appliance/access/ssh", 
                            headers=headers, 
                            json=data, 
                            verify=False)
    # Проверяем статус ответа
    if response_ssh.status_code == 200:
        print("SSH успешно разрешен.")
    else:
        print(f"Ошибка при разрешении SSH: {response_ssh.status_code} - {response_ssh.text}")

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")

# Закрытие сессии
try:

    response_close = requests.delete(f"https://{vcenter_ip}/rest/com/vmware/cis/session", 
                            headers=headers, 
                            verify=False)
    # Проверяем статус ответа
    if response_close.status_code == 200:
        print("Сессия закрыта.")
    else:
        print(f"Ошибка при закрытии сессии: {response_close.status_code} - {response_close.text}")

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")
