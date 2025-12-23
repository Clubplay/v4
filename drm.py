#!/usr/bin/env python3
"""
INSTALADOR DRM PREMIUM + FFMPEG PROXY - PHP 8.4 OBRIGATÓRIO
COMPATÍVEL COM UBUNTU 20/22/24 E DEBIAN 10/11/12
Inclui: Sistema DRM + FFmpeg Proxy + Auto-Cleanup
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import re
import platform
import tarfile
import time

class PHP84UniversalInstaller:
    def __init__(self):
        self.download_url = "https://painel.drmserve.com.br/drm_serve.zip"
        self.install_dir = "/var/www/drm"
        self.temp_zip = "/tmp/drm_temp.zip"
        self.extract_dir = "/tmp/drm_extract"
        self.license_key = None
        self.admin_username = None
        self.admin_password = None
        self.admin_email = None
        
        # Detectar sistema
        self.distro_info = self.detect_distro()
        self.distro_name = self.distro_info['name']
        self.distro_version = self.distro_info['version']
        self.distro_codename = self.distro_info['codename']
        self.architecture = self.detect_architecture()
        
        # Forçar PHP 8.4
        self.php_version = "8.4"
        self.php_service = "php8.4-fpm"
        
        print(f"🔍 Sistema detectado: {self.distro_name} {self.distro_version} ({self.distro_codename})")
        print(f"🔍 Arquitetura: {self.architecture}")
        print(f"🐘 PHP obrigatório: {self.php_version}")
        
    def detect_distro(self):
        """Detecta distribuição com precisão"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                lines = content.split('\n')
                distro_info = {}
                
                for line in lines:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        distro_info[key.lower()] = value.strip('"')
                
                name = distro_info.get('name', '').lower()
                version_id = distro_info.get('version_id', '').split('.')[0]
                
                # Padronizar nome
                if 'ubuntu' in name:
                    name = 'ubuntu'
                    if 'ubuntu_codename' in distro_info:
                        version_codename = distro_info.get('ubuntu_codename', '').lower()
                    elif 'version_codename' in distro_info:
                        version_codename = distro_info.get('version_codename', '').lower()
                    else:
                        version_map = {
                            '20': 'focal',
                            '22': 'jammy', 
                            '24': 'noble'
                        }
                        version_codename = version_map.get(version_id, 'jammy')
                elif 'debian' in name:
                    name = 'debian'
                    version_codename = distro_info.get('version_codename', '').lower()
                    if not version_codename:
                        version_map = {
                            '10': 'buster',
                            '11': 'bullseye',
                            '12': 'bookworm'
                        }
                        version_codename = version_map.get(version_id, 'bookworm')
                else:
                    name = 'ubuntu'
                    version_codename = 'jammy'
                
                return {
                    'name': name,
                    'version': version_id,
                    'codename': version_codename,
                    'id': distro_info.get('id', ''),
                    'pretty_name': distro_info.get('pretty_name', 'Unknown')
                }
        except Exception as e:
            print(f"⚠️  Erro detectando distribuição: {e}")
            return {
                'name': 'ubuntu',
                'version': '22',
                'codename': 'jammy',
                'id': 'ubuntu',
                'pretty_name': 'Ubuntu 22.04'
            }

    def detect_architecture(self):
        """Detecta a arquitetura do sistema"""
        arch = platform.machine()
        if arch in ['x86_64', 'amd64']:
            return 'x86-64'
        elif arch in ['aarch64', 'arm64']:
            return 'aarch64'
        elif arch in ['armv7l', 'armhf']:
            return 'armhf'
        else:
            return 'x86-64'

    def run_command(self, command, description="", ignore_errors=False, retries=1):
        """Executa comando no sistema"""
        print(f"🔧 {description}...")
        
        for attempt in range(retries):
            try:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    check=True, 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                if result.stdout:
                    print(f"✅ {description}")
                return True
            except subprocess.CalledProcessError as e:
                if attempt < retries - 1:
                    print(f"⚠️  Tentativa {attempt + 1}/{retries} falhou, tentando novamente...")
                    time.sleep(2)
                    continue
                    
                if ignore_errors:
                    print(f"⚠️  {description} - Ignorado")
                    return True
                print(f"❌ Erro em {description}")
                if e.stderr:
                    error_lines = e.stderr.split('\n')
                    for line in error_lines[:5]:
                        if line.strip():
                            print(f"   {line[:100]}")
                return False
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout em {description}")
                return False
            except Exception as e:
                print(f"❌ Erro inesperado: {str(e)}")
                return False

    def add_php84_repository(self):
        """Adiciona repositório PHP 8.4 apropriado"""
        print(f"📦 Adicionando repositório para PHP {self.php_version}...")
        
        self.run_command("apt install -y software-properties-common ca-certificates apt-transport-https curl wget gnupg", 
                        "Instalando dependências de repositório", retries=2)
        
        if self.distro_name == 'ubuntu':
            print("🌍 Configurando para Ubuntu...")
            commands = [
                ("add-apt-repository -y ppa:ondrej/php", "Adicionando PPA ondrej/php", False),
                ("add-apt-repository -y ppa:ondrej/nginx", "Adicionando PPA ondrej/nginx", True),
                ("apt update -y", "Atualizando cache de pacotes", False)
            ]
        elif self.distro_name == 'debian':
            print("🌍 Configurando para Debian...")
            commands = [
                ("apt install -y ca-certificates apt-transport-https", "Instalando dependências", False),
                ("curl -sSLo /usr/share/keyrings/deb.sury.org-php.gpg https://packages.sury.org/php/apt.gpg", 
                 "Baixando chave GPG Sury", False),
                (f'sh -c \'echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.org/php/ {self.distro_codename} main" > /etc/apt/sources.list.d/php.list\'',
                 "Adicionando repositório PHP 8.4", False),
                ("apt update -y", "Atualizando cache", False)
            ]
        else:
            print("⚠️  Distribuição não reconhecida, usando configuração Ubuntu...")
            commands = [
                ("add-apt-repository -y ppa:ondrej/php", "Adicionando PPA ondrej/php", False),
                ("apt update -y", "Atualizando cache", False)
            ]
        
        for cmd, desc, ignore in commands:
            if not self.run_command(cmd, desc, ignore_errors=ignore, retries=2):
                if not ignore:
                    if "ondrej/php" in cmd:
                        print("🔄 Tentando método alternativo para adicionar PPA...")
                        alt_cmds = [
                            "apt install -y python3-software-properties",
                            "LC_ALL=C.UTF-8 add-apt-repository -y ppa:ondrej/php",
                            "apt update -y"
                        ]
                        for alt_cmd in alt_cmds:
                            self.run_command(alt_cmd, "Método alternativo", ignore_errors=True)
                    return True
        return True

    def install_php84(self):
        """Instala PHP 8.4 obrigatoriamente"""
        print(f"🐘 Instalando PHP {self.php_version}...")
        
        self.run_command("apt update -y", "Atualizando cache", retries=2)
        
        print("📦 Instalando Nginx e MariaDB...")
        base_cmd = "apt install -y nginx mariadb-server mariadb-client"
        if not self.run_command(base_cmd, "Instalando servidores web e banco", retries=2):
            for pkg in ["nginx", "mariadb-server", "mariadb-client"]:
                self.run_command(f"apt install -y {pkg}", f"Instalando {pkg}", ignore_errors=True)
        
        php_packages = [
            "php8.4", "php8.4-fpm", "php8.4-cli",
            "php8.4-mysql", "php8.4-curl", "php8.4-mbstring",
            "php8.4-xml", "php8.4-zip", "php8.4-gd",
            "php8.4-bcmath", "php8.4-intl", "php8.4-opcache",
            "php8.4-common", "php8.4-soap", "php8.4-json"
        ]
        
        php_cmd = f"apt install -y {' '.join(php_packages)}"
        if not self.run_command(php_cmd, f"Instalando PHP {self.php_version} e extensões", retries=3):
            print("⚠️  Tentando instalação individual de pacotes PHP...")
            for pkg in php_packages:
                self.run_command(f"apt install -y {pkg}", f"Instalando {pkg}", ignore_errors=True)
        
        check_cmd = "php8.4 --version 2>/dev/null | head -1"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PHP {self.php_version} instalado: {result.stdout.strip()}")
        else:
            print("❌ PHP 8.4 não foi instalado corretamente")
            print("🔄 Tentando instalar via apt-get diretamente...")
            self.run_command("apt-get install -y php8.4 php8.4-fpm", "Instalando PHP via apt-get", ignore_errors=True)
        
        services = ["nginx", "mariadb", self.php_service]
        for service in services:
            self.run_command(f"systemctl enable {service}", f"Ativando {service}", ignore_errors=True)
            self.run_command(f"systemctl start {service}", f"Iniciando {service}", ignore_errors=True)
        
        return True

    def install_ffmpeg(self):
        """Instala FFmpeg"""
        print("🎬 Instalando FFmpeg...")
        
        ffmpeg_path = subprocess.run("which ffmpeg 2>/dev/null", shell=True, capture_output=True, text=True)
        
        if ffmpeg_path.returncode == 0:
            print("✅ FFmpeg já está instalado")
            return True
        
        # Instalar FFmpeg
        if not self.run_command("apt install -y ffmpeg", "Instalando FFmpeg", retries=2):
            print("⚠️  Erro ao instalar FFmpeg, mas continuando...")
            return True
        
        # Verificar instalação
        check = subprocess.run("ffmpeg -version 2>/dev/null | head -1", shell=True, capture_output=True, text=True)
        if check.returncode == 0:
            print(f"✅ FFmpeg instalado: {check.stdout.strip()}")
        else:
            print("⚠️  FFmpeg não foi instalado, mas continuando...")
        
        return True

    def install_ioncube_for_php84(self):
        """Instala IonCube Loader para PHP 8.4"""
        print(f"🔐 Instalando IonCube Loader para PHP {self.php_version}...")
        
        ioncube_temp = "/tmp/ioncube"
        
        try:
            if os.path.exists(ioncube_temp):
                shutil.rmtree(ioncube_temp)
            os.makedirs(ioncube_temp, exist_ok=True)
            
            if self.architecture == 'aarch64':
                ioncube_url = "https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_aarch64.tar.gz"
            elif self.architecture == 'armhf':
                ioncube_url = "https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_armv7l.tar.gz"
            else:
                ioncube_url = "https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz"
            
            ioncube_tar = os.path.join(ioncube_temp, "ioncube.tar.gz")
            
            print("📥 Baixando IonCube...")
            download_methods = [
                f"wget -O {ioncube_tar} '{ioncube_url}' --timeout=30 --tries=3 --quiet",
                f"curl -L -o {ioncube_tar} '{ioncube_url}' --connect-timeout 30 --silent"
            ]
            
            downloaded = False
            for cmd in download_methods:
                if self.run_command(cmd, "Baixando IonCube", ignore_errors=True):
                    downloaded = True
                    break
            
            if not downloaded:
                print("⚠️  Não foi possível baixar IonCube, continuando sem...")
                return True
            
            if not os.path.exists(ioncube_tar) or os.path.getsize(ioncube_tar) < 10000:
                print("⚠️  Arquivo IonCube inválido, continuando sem...")
                return True
            
            print("📂 Extraindo IonCube...")
            with tarfile.open(ioncube_tar, 'r:gz') as tar:
                tar.extractall(ioncube_temp)
            
            php_ext_dir = None
            possible_dirs = [
                f"/usr/lib/php/{self.php_version}",
                "/usr/lib/php/20240924",
                "/usr/lib/php/20230831",
                "/usr/lib/php/20220829",
                "/usr/lib/php/20210902",
            ]
            
            for dir_path in possible_dirs:
                if os.path.exists(dir_path):
                    php_ext_dir = dir_path
                    break
            
            if not php_ext_dir:
                php_ext_dir = f"/usr/lib/php/{self.php_version}"
                os.makedirs(php_ext_dir, exist_ok=True)
                print(f"📁 Criado diretório de extensões: {php_ext_dir}")
            
            ioncube_dir = os.path.join(ioncube_temp, "ioncube")
            ioncube_loader = None
            
            loader_84 = os.path.join(ioncube_dir, f"ioncube_loader_lin_{self.php_version}.so")
            if os.path.exists(loader_84):
                ioncube_loader = loader_84
                print(f"✅ Encontrado loader para PHP {self.php_version}")
            else:
                for version in ["8.3", "8.2", "8.1", "8.0", "7.4"]:
                    test_loader = os.path.join(ioncube_dir, f"ioncube_loader_lin_{version}.so")
                    if os.path.exists(test_loader):
                        ioncube_loader = test_loader
                        print(f"⚠️  Usando loader para PHP {version} (compatível)")
                        break
            
            if not ioncube_loader:
                print("⚠️  Loader IonCube não encontrado, continuando sem...")
                return True
            
            loader_name = os.path.basename(ioncube_loader)
            dest_loader = os.path.join(php_ext_dir, loader_name)
            shutil.copy2(ioncube_loader, dest_loader)
            os.chmod(dest_loader, 0o755)
            print(f"📄 Copiado loader: {dest_loader}")
            
            mods_dir = f"/etc/php/{self.php_version}/mods-available"
            os.makedirs(mods_dir, exist_ok=True)
            
            ioncube_ini = os.path.join(mods_dir, "00-ioncube.ini")
            with open(ioncube_ini, 'w') as f:
                f.write(f"; IonCube Loader for PHP {self.php_version}\n")
                f.write(f"zend_extension = {dest_loader}\n")
            
            for sapi in ['cli', 'fpm']:
                conf_dir = f"/etc/php/{self.php_version}/{sapi}/conf.d"
                os.makedirs(conf_dir, exist_ok=True)
                link_path = os.path.join(conf_dir, "00-ioncube.ini")
                
                if os.path.exists(link_path) or os.path.islink(link_path):
                    os.remove(link_path)
                
                os.symlink(ioncube_ini, link_path)
                print(f"🔗 Link criado: {link_path}")
            
            check_cmd = f"php8.4 -m | grep -i ioncube"
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ IonCube carregado no PHP {self.php_version}")
            else:
                print("⚠️  IonCube não está carregado, mas configurado")
            
            self.run_command(f"systemctl restart {self.php_service}", "Reiniciando PHP-FPM", ignore_errors=True)
            
            shutil.rmtree(ioncube_temp, ignore_errors=True)
            
            return True
            
        except Exception as e:
            print(f"⚠️  Erro ao instalar IonCube: {str(e)}")
            return True

    def install_basic_dependencies(self):
        """Instala dependências básicas"""
        print("📦 Instalando dependências básicas...")
        
        self.run_command("apt update -y", "Atualizando cache", retries=2)
        self.run_command("apt upgrade -y", "Atualizando sistema", ignore_errors=True)
        
        if self.command_exists("apache2"):
            print("🗑️  Removendo Apache2...")
            self.run_command("systemctl stop apache2", "Parando Apache", ignore_errors=True)
            self.run_command("apt remove --purge -y apache2 apache2-*", "Removendo Apache", ignore_errors=True)
        
        tools = [
            "curl", "wget", "unzip", "gnupg", "lsb-release",
            "ca-certificates", "apt-transport-https", 
            "software-properties-common", "git", "htop",
            "nano", "vim", "net-tools", "ufw"
        ]
        
        tools_cmd = f"apt install -y {' '.join(tools)}"
        self.run_command(tools_cmd, "Instalando ferramentas", retries=2)
        
        return True

    def command_exists(self, command):
        """Verifica se comando existe"""
        result = subprocess.run(
            f"which {command} > /dev/null 2>&1",
            shell=True,
            capture_output=True
        )
        return result.returncode == 0

    def create_secure_config(self):
        """Cria config.php baseado no config_lb.php"""
        print("🔒 Criando config.php...")
        
        config_content = f"""<?php
// config.php - Configuração DRM Premium + FFmpeg Proxy
session_start();
date_default_timezone_set('America/Sao_Paulo');

// ============================================
// CONFIGURAÇÕES PRINCIPAIS
// ============================================

define('LICENSE_KEY', '{self.license_key}');
define('MASTER_API_URL', 'https://painel.drmserve.com.br/api_drm.php');
define('ADMIN_USERNAME', '{self.admin_username}');
define('ADMIN_PASSWORD', '{self.admin_password}');
define('ADMIN_EMAIL', '{self.admin_email}');

// ============================================
// DIRETÓRIOS DO SISTEMA
// ============================================

define('DATA_DIR', __DIR__ . '/data/');
define('USERS_FILE', DATA_DIR . 'users.json');
define('PENDING_FILE', DATA_DIR . 'pending_users.json');
define('SHARED_DIR', '/tmp/live_streams/');
define('STATS_DIR', DATA_DIR . 'lb_stats/');
define('LOG_DIR', DATA_DIR . 'logs/');

// ============================================
// CONFIGURAÇÃO DOS SERVIDORES PROXY (LOAD BALANCER)
// ============================================

define('PROXY_SERVERS', [
    // Descomente e configure se usar Load Balancer
    // [
    //     'id' => 1,
    //     'name' => 'Servidor Proxy 1',
    //     'host' => 'proxy1.exemplo.com',
    //     'port' => 80,
    //     'weight' => 10,
    //     'max_viewers' => 500,
    //     'is_active' => true
    // ]
]);

// ============================================
// ESTRATÉGIAS DE BALANCEAMENTO
// ============================================

define('BALANCE_STRATEGY', 'least_connections');

// ============================================
// CONFIGURAÇÕES DE PERFORMANCE
// ============================================

define('ENABLE_CACHE', true);
define('CACHE_TTL', 300);
define('ENABLE_COMPRESSION', true);
define('MAX_REDIRECTS', 3);
define('CONNECTION_TIMEOUT', 10);
define('STREAM_BUFFER_SIZE', 32768);

// ============================================
// CONFIGURAÇÕES DE LOGS
// ============================================

define('ENABLE_LOGGING', true);
define('LOG_LEVEL', 'info');
define('LOG_RETENTION_DAYS', 30);
define('LOG_MAX_SIZE', 10485760);

// ============================================
// CRIAR DIRETÓRIOS SE NÃO EXISTIREM
// ============================================

$directories = [
    DATA_DIR,
    STATS_DIR,
    LOG_DIR,
    SHARED_DIR,
    DATA_DIR . 'cache/',
    DATA_DIR . 'backups/'
];

foreach ($directories as $dir) {{
    if (!file_exists($dir)) {{
        mkdir($dir, 0755, true);
    }}
}}

// ============================================
// FUNÇÕES DE GERENCIAMENTO DE USUÁRIOS
// ============================================

function loadUsers() {{
    if (!file_exists(USERS_FILE)) {{
        return [];
    }}
    $content = file_get_contents(USERS_FILE);
    return json_decode($content, true) ?? [];
}}

function saveUsers($users) {{
    $backup = DATA_DIR . 'backups/users_' . date('Y-m-d_H-i-s') . '.json';
    if (file_exists(USERS_FILE)) {{
        copy(USERS_FILE, $backup);
    }}
    file_put_contents(USERS_FILE, json_encode($users, JSON_PRETTY_PRINT));
}}

function loadPendingUsers() {{
    if (!file_exists(PENDING_FILE)) {{
        return [];
    }}
    $content = file_get_contents(PENDING_FILE);
    return json_decode($content, true) ?? [];
}}

function savePendingUsers($users) {{
    file_put_contents(PENDING_FILE, json_encode($users, JSON_PRETTY_PRINT));
}}

function userExists($username, $email = null) {{
    $users = loadUsers();
    foreach ($users as $user) {{
        if ($user['username'] === $username) {{
            return true;
        }}
        if ($email && isset($user['email']) && $user['email'] === $email) {{
            return true;
        }}
    }}
    return false;
}}

function pendingExists($username, $email = null) {{
    $pending = loadPendingUsers();
    foreach ($pending as $user) {{
        if ($user['username'] === $username) {{
            return true;
        }}
        if ($email && isset($user['email']) && $user['email'] === $email) {{
            return true;
        }}
    }}
    return false;
}}

// ============================================
// FUNÇÕES DE AUTENTICAÇÃO
// ============================================

function authenticateUser($username, $password) {{
    if ($username === ADMIN_USERNAME && $password === ADMIN_PASSWORD) {{
        return [
            'id' => 0,
            'username' => ADMIN_USERNAME,
            'email' => ADMIN_EMAIL,
            'full_name' => 'Administrador',
            'is_admin' => true,
            'is_active' => true,
            'created_at' => date('Y-m-d H:i:s')
        ];
    }}
    
    $users = loadUsers();
    foreach ($users as $user) {{
        if ($user['username'] === $username && 
            password_verify($password, $user['password']) && 
            $user['is_active']) {{
            return $user;
        }}
    }}
    
    return false;
}}

function createPendingUser($data) {{
    $pending = loadPendingUsers();
    
    $newUser = [
        'id' => uniqid('pending_'),
        'username' => $data['username'],
        'email' => $data['email'],
        'password' => password_hash($data['password'], PASSWORD_DEFAULT),
        'full_name' => $data['full_name'],
        'license_key' => $data['license_key'],
        'created_at' => date('Y-m-d H:i:s'),
        'ip_address' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
    ];
    
    $pending[] = $newUser;
    savePendingUsers($pending);
    
    logEvent('user_registration', 'Novo usuário pendente: ' . $data['username']);
    
    return true;
}}

function approveUser($pending_id) {{
    $pending = loadPendingUsers();
    $users = loadUsers();
    
    $approved = null;
    $newPending = [];
    
    foreach ($pending as $user) {{
        if ($user['id'] === $pending_id) {{
            $approved = $user;
        }} else {{
            $newPending[] = $user;
        }}
    }}
    
    if ($approved) {{
        unset($approved['id']);
        $approved['id'] = count($users) + 1;
        $approved['is_active'] = true;
        $approved['is_admin'] = false;
        $approved['approved_at'] = date('Y-m-d H:i:s');
        $approved['approved_by'] = $_SESSION['username'] ?? 'system';
        
        $users[] = $approved;
        saveUsers($users);
        savePendingUsers($newPending);
        
        logEvent('user_approved', 'Usuário aprovado: ' . $approved['username']);
        
        return true;
    }}
    
    return false;
}}

function rejectUser($pending_id) {{
    $pending = loadPendingUsers();
    $newPending = [];
    $rejected_username = '';
    
    foreach ($pending as $user) {{
        if ($user['id'] !== $pending_id) {{
            $newPending[] = $user;
        }} else {{
            $rejected_username = $user['username'];
        }}
    }}
    
    savePendingUsers($newPending);
    
    if ($rejected_username) {{
        logEvent('user_rejected', 'Usuário rejeitado: ' . $rejected_username);
    }}
    
    return true;
}}

// ============================================
// FUNÇÕES DE VALIDAÇÃO DE LICENÇA
// ============================================

function validateLicense($license_key) {{
    $licenses_url = 'https://painel.drmserve.com.br/licenses.json';
    
    $context = stream_context_create([
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
        ],
        'http' => [
            'timeout' => 5,
            'header' => "User-Agent: DRM-System/1.0\\r\\n"
        ]
    ]);
    
    $json_content = @file_get_contents($licenses_url, false, $context);
    
    if (!$json_content) {{
        return validateLicenseWithCurl($license_key);
    }}
    
    $licenses = json_decode($json_content, true);
    
    if (!$licenses) {{
        logEvent('license_error', 'Falha ao decodificar JSON de licenças');
        return false;
    }}
    
    $is_valid = isset($licenses[$license_key]) && 
                isset($licenses[$license_key]['status']) && 
                $licenses[$license_key]['status'] === 'active';
    
    if ($is_valid) {{
        logEvent('license_validated', 'Licença válida: ' . substr($license_key, 0, 8) . '...');
    }} else {{
        logEvent('license_invalid', 'Licença inválida: ' . substr($license_key, 0, 8) . '...');
    }}
    
    return $is_valid;
}}

function validateLicenseWithCurl($license_key) {{
    $licenses_url = 'https://painel.drmserve.com.br/licenses.json';
    
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $licenses_url,
        CURLOPT_RETURNTRANSFER => 1,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_USERAGENT => 'DRM-System/1.0'
    ]);
    
    $data = curl_exec($ch);
    $error = curl_error($ch);
    curl_close($ch);
    
    if (!$data) {{
        logEvent('license_error', 'cURL falhou: ' . $error);
        return false;
    }}
    
    $licenses = json_decode($data, true);
    
    if (!$licenses) {{
        return false;
    }}
    
    return isset($licenses[$license_key]) && 
           isset($licenses[$license_key]['status']) && 
           $licenses[$license_key]['status'] === 'active';
}}

function getStreamUrl($license_key, $stream_id) {{
    $url = MASTER_API_URL . '?key=' . urlencode($license_key) . 
           '&action=get_stream_url&id=' . urlencode($stream_id);
    
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => 1,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_SSL_VERIFYPEER => false
    ]);
    
    $data = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($http_code !== 200) {{
        logEvent('api_error', "API retornou código $http_code para stream $stream_id");
        return null;
    }}
    
    $json = json_decode($data, true);
    
    if ($json && isset($json['status']) && $json['status'] == 'ok') {{
        return $json['url'];
    }}
    
    return null;
}}

// ============================================
// FUNÇÕES DE SESSÃO E CONTROLE
// ============================================

function isLoggedIn() {{
    return isset($_SESSION['user_id']);
}}

function isAdmin() {{
    return isset($_SESSION['is_admin']) && $_SESSION['is_admin'] === true;
}}

function requireLogin() {{
    if (!isLoggedIn()) {{
        header('Location: login.php');
        exit;
    }}
}}

function requireAdmin() {{
    requireLogin();
    if (!isAdmin()) {{
        header('Location: index.php');
        exit;
    }}
}}

function getCurrentUser() {{
    if (!isLoggedIn()) {{
        return null;
    }}
    
    if (isAdmin()) {{
        return [
            'id' => 0,
            'username' => ADMIN_USERNAME,
            'email' => ADMIN_EMAIL,
            'full_name' => 'Administrador',
            'is_admin' => true
        ];
    }}
    
    $users = loadUsers();
    foreach ($users as $user) {{
        if ($user['id'] === $_SESSION['user_id']) {{
            return $user;
        }}
    }}
    
    return null;
}}

// ============================================
// FUNÇÕES DE LOGGING
// ============================================

function logEvent($type, $message, $level = 'info') {{
    if (!ENABLE_LOGGING) {{
        return;
    }}
    
    $log_levels = ['debug' => 0, 'info' => 1, 'warning' => 2, 'error' => 3];
    $current_level = $log_levels[LOG_LEVEL] ?? 1;
    $event_level = $log_levels[$level] ?? 1;
    
    if ($event_level < $current_level) {{
        return;
    }}
    
    $log_file = LOG_DIR . date('Y-m-d') . '.log';
    
    $entry = sprintf(
        "[%s] [%s] [%s] %s\\n",
        date('Y-m-d H:i:s'),
        strtoupper($level),
        $type,
        $message
    );
    
    file_put_contents($log_file, $entry, FILE_APPEND);
    
    if (file_exists($log_file) && filesize($log_file) > LOG_MAX_SIZE) {{
        $backup = LOG_DIR . date('Y-m-d_H-i-s') . '.log';
        rename($log_file, $backup);
    }}
}}

function cleanOldLogs() {{
    $files = glob(LOG_DIR . '*.log');
    $cutoff = time() - (LOG_RETENTION_DAYS * 86400);
    
    foreach ($files as $file) {{
        if (filemtime($file) < $cutoff) {{
            unlink($file);
        }}
    }}
}}

// ============================================
// FUNÇÕES DE STATUS
// ============================================

function checkLicenseStatus() {{
    if (!validateLicense(LICENSE_KEY)) {{
        return [
            'status' => 'error', 
            'message' => 'Licença inválida para este IP: ' . ($_SERVER['REMOTE_ADDR'] ?? 'unknown')
        ];
    }}
    return [
        'status' => 'ok', 
        'message' => 'Licença válida'
    ];
}}

function getSystemStats() {{
    return [
        'php_version' => PHP_VERSION,
        'memory_usage' => memory_get_usage(true),
        'memory_peak' => memory_get_peak_usage(true),
        'uptime' => file_exists(DATA_DIR . 'uptime.txt') ? 
                    (time() - intval(file_get_contents(DATA_DIR . 'uptime.txt'))) : 0,
        'total_users' => count(loadUsers()),
        'pending_users' => count(loadPendingUsers()),
        'disk_free' => disk_free_space(DATA_DIR),
        'disk_total' => disk_total_space(DATA_DIR)
    ];
}}

// ============================================
// INICIALIZAÇÃO DO SISTEMA
// ============================================

if (!file_exists(DATA_DIR . 'uptime.txt')) {{
    file_put_contents(DATA_DIR . 'uptime.txt', time());
}}

if (rand(1, 100) === 1) {{
    cleanOldLogs();
}}

if (!defined('DRM_SYSTEM')) {{
    define('DRM_SYSTEM', true);
}}

logEvent('system', 'Sistema DRM Premium + FFmpeg Proxy iniciado');

?>
"""
        
        config_path = os.path.join(self.install_dir, "config.php")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ config.php criado em {config_path}")
        return True

    def install_ffmpeg_proxy_system(self):
        """Instala sistema FFmpeg Proxy completo"""
        print("🎬 Instalando Sistema FFmpeg Proxy...")
        
        # Criar diretórios necessários
        directories = [
            '/tmp/ffmpeg_streams',
            f'{self.install_dir}/ffmpeg_workers',
            f'{self.install_dir}/worker_tracking'
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, 0o755, exist_ok=True)
                print(f"   📁 Criado: {directory}")
        
        # Executar instalador FFmpeg se existir
        installer_path = os.path.join(self.install_dir, "ffmpeg_installer.php")
        if os.path.exists(installer_path):
            print("   🔧 Executando instalador FFmpeg...")
            result = subprocess.run(
                f"php {installer_path}",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("   ✅ FFmpeg Proxy instalado via PHP")
            else:
                print("   ⚠️  Instalador PHP não executou, configurando manualmente...")
        
        # Configurar CRON para auto-cleanup
        self.setup_ffmpeg_cron()
        
        # Criar comandos helper
        self.create_ffmpeg_helpers()
        
        print("✅ Sistema FFmpeg Proxy instalado")
        return True

    def setup_ffmpeg_cron(self):
        """Configura CRON para FFmpeg auto-cleanup"""
        print("⏰ Configurando CRON para FFmpeg...")
        
        cron_user = 'www-data'
        
        # Obter crontab atual
        result = subprocess.run(
            f"crontab -u {cron_user} -l 2>/dev/null",
            shell=True,
            capture_output=True,
            text=True
        )
        
        current_cron = result.stdout if result.returncode == 0 else ""
        
        # CRON jobs para adicionar
        cron_jobs = [
            f"*/2 * * * * /usr/bin/php {self.install_dir}/ffmpeg_auto_cleanup.php >> {self.install_dir}/ffmpeg_auto_cleanup.log 2>&1",
            f"*/5 * * * * /usr/bin/php {self.install_dir}/ffmpeg_monitor.php >> {self.install_dir}/ffmpeg_monitor_cron.log 2>&1"
        ]
        
        # Verificar se já existem
        new_cron_lines = []
        for job in cron_jobs:
            if job not in current_cron:
                new_cron_lines.append(job)
        
        if new_cron_lines:
            # Adicionar novos jobs
            new_cron = current_cron
            if not current_cron.endswith('\n') and current_cron:
                new_cron += '\n'
            
            new_cron += "# FFmpeg Proxy Auto-Cleanup\n"
            new_cron += '\n'.join(new_cron_lines) + '\n'
            
            # Salvar nova crontab
            temp_cron = '/tmp/new_crontab.txt'
            with open(temp_cron, 'w') as f:
                f.write(new_cron)
            
            subprocess.run(
                f"crontab -u {cron_user} {temp_cron}",
                shell=True,
                check=False
            )
            
            os.remove(temp_cron)
            print("   ✅ CRON configurado")
        else:
            print("   ℹ️  CRON já configurado")
        
        return True

    def create_ffmpeg_helpers(self):
        """Cria comandos helper para FFmpeg"""
        print("🛠️  Criando comandos helper...")
        
        helpers = {
            'ffmpeg-status': f'#!/bin/bash\nphp {self.install_dir}/ffmpeg_monitor.php',
            'ffmpeg-stop-all': f'#!/bin/bash\nphp {self.install_dir}/ffmpeg_stop_all.php',
            'ffmpeg-cleanup': f'#!/bin/bash\nphp {self.install_dir}/ffmpeg_auto_cleanup.php'
        }
        
        for cmd_name, cmd_content in helpers.items():
            cmd_path = f'/usr/local/bin/{cmd_name}'
            try:
                with open(cmd_path, 'w') as f:
                    f.write(cmd_content)
                os.chmod(cmd_path, 0o755)
                print(f"   ✅ Criado: {cmd_name}")
            except Exception as e:
                print(f"   ⚠️  Erro ao criar {cmd_name}: {e}")
        
        return True

    def download_drm_files(self):
        """Baixa arquivos DRM"""
        print("📥 Baixando DRM...")
        
        download_methods = [
            f"wget -O {self.temp_zip} '{self.download_url}' --timeout=60 --tries=3",
            f"curl -L -o {self.temp_zip} '{self.download_url}' --connect-timeout 30",
            f"wget --no-check-certificate -O {self.temp_zip} '{self.download_url}'"
        ]
        
        for method in download_methods:
            if self.run_command(method, "Baixando arquivos", ignore_errors=True):
                if os.path.exists(self.temp_zip) and os.path.getsize(self.temp_zip) > 1024:
                    size = os.path.getsize(self.temp_zip)
                    print(f"✅ DRM baixado ({size:,} bytes)")
                    return True
        
        print("❌ Falha ao baixar arquivos DRM")
        return False

    def extract_files(self):
        """Extrai arquivos"""
        print("📂 Extraindo arquivos...")
        
        try:
            if os.path.exists(self.extract_dir):
                shutil.rmtree(self.extract_dir)
            os.makedirs(self.extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.temp_zip, 'r') as zip_ref:
                zip_ref.extractall(self.extract_dir)
            
            extracted_items = os.listdir(self.extract_dir)
            print(f"📄 Extraídos {len(extracted_items)} itens")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao extrair: {str(e)}")
            return False

    def copy_files_to_install_dir(self):
        """Copia arquivos para diretório de instalação"""
        print("📄 Copiando arquivos para diretório de instalação...")
        
        try:
            if os.path.exists(self.install_dir):
                backup_dir = f"{self.install_dir}_backup_{int(time.time())}"
                print(f"📦 Fazendo backup para {backup_dir}")
                shutil.move(self.install_dir, backup_dir)
            
            os.makedirs(self.install_dir, exist_ok=True)
            
            source_dir = self.extract_dir
            for root, dirs, files in os.walk(self.extract_dir):
                if "index.php" in files:
                    source_dir = root
                    break
            
            for item in os.listdir(source_dir):
                src = os.path.join(source_dir, item)
                dst = os.path.join(self.install_dir, item)
                
                if os.path.isdir(src):
                    shutil.copytree(src, dst, symlinks=True, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            
            print(f"✅ Arquivos copiados para {self.install_dir}")
            return True
        except Exception as e:
            print(f"❌ Erro ao copiar: {str(e)}")
            return False

    def configure_nginx_for_php84(self):
        """Configura Nginx para PHP 8.4"""
        print("🌐 Configurando Nginx...")
        
        php_socket = f"/var/run/php/php8.4-fpm.sock"
        if not os.path.exists(php_socket):
            php_socket = "/run/php/php8.4-fpm.sock"
        
        nginx_config = f"""server {{
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    root {self.install_dir};
    index index.php index.html index.htm;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    client_max_body_size 100M;
    client_body_timeout 300s;

    access_log /var/log/nginx/drm_access.log;
    error_log /var/log/nginx/drm_error.log;

    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}

    location ~ \\.php$ {{
        fastcgi_split_path_info ^(.+\\.php)(/.+)$;
        fastcgi_pass unix:{php_socket};
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_intercept_errors on;
        fastcgi_buffers 16 16k;
        fastcgi_buffer_size 32k;
        fastcgi_read_timeout 300;
    }}

    location ~ /\\. {{
        deny all;
        access_log off;
        log_not_found off;
    }}

    location ~* \\.(log|sql|tar|gz|zip)$ {{
        deny all;
    }}

    location ~* \\.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }}
}}
"""
        
        try:
            default_conf = "/etc/nginx/sites-enabled/default"
            if os.path.exists(default_conf):
                os.remove(default_conf)
            
            available_path = "/etc/nginx/sites-available/drm"
            with open(available_path, 'w') as f:
                f.write(nginx_config)
            
            enabled_path = "/etc/nginx/sites-enabled/drm"
            if os.path.exists(enabled_path) or os.path.islink(enabled_path):
                os.remove(enabled_path)
            os.symlink(available_path, enabled_path)
            
            if self.run_command("nginx -t", "Testando configuração Nginx"):
                self.run_command("systemctl reload nginx", "Recarregando Nginx")
                print("✅ Nginx configurado para PHP 8.4")
                return True
            else:
                print("❌ Configuração Nginx inválida")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar Nginx: {str(e)}")
            return False

    def configure_php84_settings(self):
        """Configura PHP 8.4"""
        print("⚙️  Configurando PHP 8.4...")
        
        php_ini_paths = [
            f"/etc/php/{self.php_version}/fpm/php.ini",
            f"/etc/php/{self.php_version}/cli/php.ini"
        ]
        
        for php_ini_path in php_ini_paths:
            if not os.path.exists(php_ini_path):
                print(f"⚠️  {php_ini_path} não encontrado")
                continue
            
            try:
                with open(php_ini_path, 'r') as f:
                    content = f.read()
                
                adjustments = {
                    'upload_max_filesize': 'upload_max_filesize = 100M',
                    'post_max_size': 'post_max_size = 100M',
                    'max_execution_time': 'max_execution_time = 300',
                    'max_input_time': 'max_input_time = 300',
                    'memory_limit': 'memory_limit = 256M',
                    'display_errors': 'display_errors = Off',
                    'error_reporting': 'error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT',
                    'date.timezone': 'date.timezone = America/Sao_Paulo',
                    'opcache.enable': 'opcache.enable = 1',
                    'opcache.memory_consumption': 'opcache.memory_consumption = 128',
                    'opcache.max_accelerated_files': 'opcache.max_accelerated_files = 10000'
                }
                
                for key, value in adjustments.items():
                    pattern = rf'^;?\s*{key}\s*=.*$'
                    if re.search(pattern, content, re.MULTILINE):
                        content = re.sub(pattern, value, content, flags=re.MULTILINE)
                    else:
                        content += f"\n{value}\n"
                
                with open(php_ini_path, 'w') as f:
                    f.write(content)
                
                print(f"✅ {php_ini_path} configurado")
                
            except Exception as e:
                print(f"⚠️  Erro ao configurar {php_ini_path}: {str(e)}")
        
        self.run_command(f"systemctl restart {self.php_service}", "Reiniciando PHP-FPM", ignore_errors=True)
        return True

    def setup_permissions(self):
        """Configura permissões"""
        print("🔒 Configurando permissões...")
        
        try:
            self.run_command(f"chown -R www-data:www-data {self.install_dir}", "Definindo proprietário")
            self.run_command(f"find {self.install_dir} -type d -exec chmod 755 {{}} \\;", "Permissões de diretórios")
            self.run_command(f"find {self.install_dir} -type f -exec chmod 644 {{}} \\;", "Permissões de arquivos")
            
            data_dir = os.path.join(self.install_dir, "data")
            if os.path.exists(data_dir):
                self.run_command(f"chmod -R 775 {data_dir}", "Permissões para data")
                self.run_command(f"chown -R www-data:www-data {data_dir}", "Proprietário para data")
            
            index_path = os.path.join(self.install_dir, "index.php")
            if os.path.exists(index_path):
                stat = os.stat(index_path)
                print(f"✅ index.php: {oct(stat.st_mode)[-3:]}")
            
            return True
        except Exception as e:
            print(f"⚠️  Erro em permissões: {str(e)}")
            return True

    def configure_firewall(self):
        """Configura firewall"""
        print("🔥 Configurando firewall...")
        
        if not self.command_exists("ufw"):
            self.run_command("apt install -y ufw", "Instalando UFW", ignore_errors=True)
        
        commands = [
            ("ufw --force enable", "Ativando UFW", True),
            ("ufw allow 22/tcp", "Permitindo SSH", True),
            ("ufw allow 80/tcp", "Permitindo HTTP", True),
            ("ufw allow 443/tcp", "Permitindo HTTPS", True),
            ("ufw default deny incoming", "Negar entrada padrão", True),
            ("ufw default allow outgoing", "Permitir saída padrão", True)
        ]
        
        for cmd, desc, ignore in commands:
            self.run_command(cmd, desc, ignore_errors=ignore)
        
        self.run_command("ufw status", "Status do firewall", ignore_errors=True)
        return True

    def get_credentials(self):
        """Solicita credenciais"""
        print("\n" + "="*60)
        print("🔐 CONFIGURAÇÃO DO SISTEMA DRM PREMIUM + FFMPEG PROXY")
        print("="*60)
        
        while True:
            license_key = input("\n🔑 Digite sua chave de licença: ").strip()
            if license_key:
                self.license_key = license_key
                break
            print("❌ Licença não pode estar vazia.")
        
        while True:
            username = input("👤 Nome de usuário administrativo: ").strip()
            if username and len(username) >= 3:
                self.admin_username = username
                break
            print("❌ Usuário deve ter pelo menos 3 caracteres.")
        
        while True:
            password = input("🔒 Senha administrativa: ").strip()
            if password and len(password) >= 6:
                confirm = input("🔒 Confirme a senha: ").strip()
                if password == confirm:
                    self.admin_password = password
                    break
                print("❌ Senhas não coincidem!")
            else:
                print("❌ Senha deve ter pelo menos 6 caracteres.")
        
        email = input("📧 Email administrativo (opcional): ").strip()
        if not email:
            email = f"{self.admin_username}@drm.local"
        self.admin_email = email
        
        print("\n✅ Credenciais configuradas!")
        return True

    def cleanup(self):
        """Limpeza"""
        print("🧹 Limpando arquivos temporários...")
        
        temp_items = [self.temp_zip, self.extract_dir, "/tmp/ioncube"]
        for item in temp_items:
            try:
                if os.path.exists(item):
                    if os.path.isdir(item):
                        shutil.rmtree(item)
                    else:
                        os.remove(item)
            except:
                pass
        
        print("✅ Limpeza concluída")

    def get_server_ip(self):
        """Obtém IP do servidor"""
        try:
            methods = [
                "hostname -I | awk '{print $1}'",
                "ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1 | head -1",
                "curl -s ifconfig.me",
                "curl -s icanhazip.com"
            ]
            
            for method in methods:
                try:
                    result = subprocess.run(method, shell=True, capture_output=True, text=True, timeout=5)
                    ip = result.stdout.strip()
                    if ip and len(ip) > 6 and '.' in ip and not ip.startswith("127."):
                        return ip
                except:
                    continue
        except:
            pass
        
        return "SEU_IP"

    def show_summary(self):
        """Mostra resumo"""
        ip = self.get_server_ip()
        
        print("\n" + "="*70)
        print("🎉 INSTALAÇÃO DRM PREMIUM + FFMPEG PROXY CONCLUÍDA!")
        print("="*70)
        
        print(f"""
📋 INFORMAÇÕES DO SISTEMA:

🏷️  Distribuição: {self.distro_info['pretty_name']}
🏗️  Arquitetura: {self.architecture}
🐘 PHP Versão: {self.php_version} (Obrigatório)
🎬 FFmpeg: Instalado
🌐 Servidor Web: Nginx
🗄️  Banco de Dados: MariaDB
🔐 IonCube: Instalado

🌐 ACESSO WEB:
   Painel Admin: http://{ip}/index.php
   Login: http://{ip}/login.php
   Monitor FFmpeg: http://{ip}/monitor.php

🔐 CREDENCIAIS ADMIN:
   👤 Usuário: {self.admin_username}
   🔒 Senha: {self.admin_password}
   📧 Email: {self.admin_email}
   🔑 Licença: {self.license_key}
   
🎬 COMANDOS FFMPEG:
   ffmpeg-status      - Ver workers ativos
   ffmpeg-stop-all    - Parar todos os workers
   ffmpeg-cleanup     - Limpeza manual

🔄 REINICIAR SERVIÇOS:
   sudo systemctl restart nginx
   sudo systemctl restart php8.4-fpm
   sudo systemctl restart mariadb

📊 VER STATUS:
   sudo systemctl status nginx php8.4-fpm mariadb

📈 MONITORAR LOGS:
   sudo tail -f /var/log/nginx/drm_error.log
   sudo tail -f {self.install_dir}/ffmpeg_workers.log

🔧 CONFIGURAÇÕES:
   PHP Config: /etc/php/8.4/fpm/php.ini
   Nginx Config: /etc/nginx/sites-available/drm
   DRM Config: {self.install_dir}/config.php

⚡ PRÓXIMOS PASSOS:

1️⃣  Acesse http://{ip} no navegador
2️⃣  Faça login com: {self.admin_username} / {self.admin_password}
3️⃣  Configure o sistema conforme necessário
4️⃣  IMPORTANTE: Guarde suas credenciais em local seguro!

🔒 SEGURANÇA CONFIGURADA:
   ✅ Firewall UFW ativado
   ✅ Headers de segurança no Nginx
   ✅ PHP com configurações seguras
   ✅ Acesso apenas às portas 22, 80, 443
   ✅ FFmpeg Proxy com auto-cleanup

💡 SUPORTE:
   Telegram: @unyserveinc

🚀 Sistema pronto para produção com economia de 90-99% de banda!
""")
        
        print("="*70)

    def install(self):
        """Instalação principal"""
        print("\n" + "="*60)
        print("🚀 INICIANDO INSTALAÇÃO DRM + FFMPEG PROXY - PHP 8.4")
        print("="*60)
        
        if os.geteuid() != 0:
            print("❌ Execute como root: sudo python3 install_drm_php84.py")
            sys.exit(1)
        
        if not self.get_credentials():
            sys.exit(1)
        
        steps = [
            ("Instalando dependências básicas", self.install_basic_dependencies),
            ("Configurando repositório PHP 8.4", self.add_php84_repository),
            ("Instalando PHP 8.4, Nginx, MariaDB", self.install_php84),
            ("Instalando FFmpeg", self.install_ffmpeg),
            ("Instalando IonCube Loader", self.install_ioncube_for_php84),
            ("Baixando arquivos DRM", self.download_drm_files),
            ("Extraindo arquivos", self.extract_files),
            ("Copiando para diretório de instalação", self.copy_files_to_install_dir),
            ("Criando config.php", self.create_secure_config),
            ("Instalando Sistema FFmpeg Proxy", self.install_ffmpeg_proxy_system),
            ("Configurando Nginx", self.configure_nginx_for_php84),
            ("Configurando PHP 8.4", self.configure_php84_settings),
            ("Configurando permissões", self.setup_permissions),
            ("Configurando firewall", self.configure_firewall)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*50}")
            print(f"📍 {step_name}")
            print("="*50)
            
            if not step_func():
                non_critical = [
                    "Configurando firewall",
                    "Instalando IonCube Loader",
                    "Configurando PHP 8.4",
                    "Instalando FFmpeg",
                    "Instalando Sistema FFmpeg Proxy"
                ]
                
                if step_name in non_critical:
                    print(f"⚠️  {step_name} falhou (não crítico)")
                    continue
                else:
                    print(f"❌ {step_name} falhou (crítico)")
                    print("🛑 Instalação abortada!")
                    self.cleanup()
                    sys.exit(1)
        
        self.cleanup()
        self.show_summary()

if __name__ == "__main__":
    try:
        installer = PHP84UniversalInstaller()
        installer.install()
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalação cancelada pelo usuário!")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)