# Monitoramento da Temperatura do Rio com Airflow, Docker e PostgreSQL

Este projeto implementa um sistema de monitoramento da temperatura do rio utilizando **Apache Airflow**, **Docker** e **PostgreSQL**. A solução orquestra um fluxo de trabalho para extrair dados de temperatura de um arquivo JSON, realizar verificações condicionais com base nos valores de temperatura e, dependendo do resultado, realizar diferentes ações (enviar alertas por e-mail ou armazenar dados em um banco de dados PostgreSQL).

## Visão Geral

A DAG do Airflow implementa as seguintes etapas principais:

- **Sensor de Arquivo (FileSensor)**: Aguarda a chegada de um arquivo JSON com dados de temperatura.
- **Extração de Dados (PythonOperator)**: Extrai o ID do rio, temperatura e timestamp do arquivo JSON.
- **Verificação de Temperatura (BranchPythonOperator)**: Verifica se a temperatura está dentro de um intervalo aceitável (10°C - 25°C) e direciona o fluxo de trabalho para diferentes ramos (*branching*).
- **Envio de E-mails (EmailOperator)**: Se a temperatura estiver fora dos limites, um alerta por e-mail é enviado. Caso contrário, um e-mail de confirmação é enviado.
- **Armazenamento em Banco de Dados (PostgresOperator)**: Criação de uma tabela no PostgreSQL e inserção dos dados extraídos do arquivo JSON.

## Tecnologias Utilizadas

- **Apache Airflow**: Orquestração de workflows e automação de tarefas.
- **Docker**: Containerização para garantir ambientes consistentes de execução.
- **PostgreSQL**: Banco de dados relacional para armazenamento de dados.
- **Python**: Implementação da lógica de extração e verificação dos dados.
- **XComs (Cross-communication)**: Compartilhamento de dados entre tarefas da DAG.
- **Branching**: Direcionamento condicional do fluxo de tarefas baseado em regras de negócio.


##  Requisitos

- Docker e Docker Compose instalados.
- Apache Airflow configurado corretamente em contêiner Docker.
  

##  Conclusão

Este projeto é um exemplo prático de como utilizar o Apache Airflow para criar um fluxo de trabalho automatizado com **sensor de arquivos**, **extração de dados**, **decisão condicional com branching**, **envio de alertas por e-mail** e **armazenamento em banco de dados**.

Ao utilizar **XComs**, os dados são compartilhados de forma transparente entre tarefas, garantindo modularidade e clareza no fluxo. O uso de **Branching** permite decisões lógicas dinâmicas com base no conteúdo dos dados monitorados.
