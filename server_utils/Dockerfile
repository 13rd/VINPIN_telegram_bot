# Базовый образ CentOS 7
FROM centos:7

# Обновление системы
RUN yum -y update

# Установка необходимых пакетов
RUN yum -y install openssh-server passwd

# Очистка кэша
RUN yum clean all

# Создание директории для SSH
RUN mkdir /var/run/sshd

# Установка пароля для root (замените 'your_password' на ваш пароль)
RUN echo 'root:pass' | chpasswd

# Разрешение входа через SSH для root
RUN sed -i 's/^#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config

# Отключение DNS-проверки (для ускорения подключения)
RUN sed -i 's/^#UseDNS yes/UseDNS no/' /etc/ssh/sshd_config

# Порт SSH
EXPOSE 22

# Команда для запуска SSH-сервера
CMD ["/usr/sbin/sshd", "-D"]