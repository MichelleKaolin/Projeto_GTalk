# 📢 GTalk - Conversão de Áudio para Texto com IA

## 📌 Visão Geral

**GTalk** é uma extensão que utiliza Inteligência Artificial para transcrever áudios em texto de forma rápida e precisa. A ideia é integrar o projeto com **GeniUs**, criando um banco de dados de resumos de áudio que serão utilizados para aprimorar as questões de quiz e oferecer uma experiência de aprendizado mais dinâmica e acessível. Além disso, o **GTalk** facilita a criação de notas de estudo a partir de qualquer conteúdo falado.

## 🎯 Objetivos
- **Transcrever áudios em texto** de maneira eficiente utilizando IA.
- **Integrar com o GeniUs**, criando um banco de dados de conteúdo que aprimora as questões de quiz.
- **Facilitar o estudo**, permitindo que os alunos transformem áudios de aulas, palestras ou podcasts em texto.
- **Criar uma interface simples e amigável** para facilitar o uso tanto em dispositivos móveis quanto desktop.

## 🎯 Funcionalidades
- 📌 **Gravação de Áudio:** Captura de áudios diretamente no aplicativo ou através de uploads.
- 📌 **Transcrição Instantânea:** O áudio é convertido em texto automaticamente.
- 📌 **Armazenamento de Texto:** O texto transcrito é salvo em um banco de dados, criando uma base de conteúdo.
- 📌 **Integração com GeniUs:** O texto gerado é utilizado para criar questões de quiz e desafios diários.
- 📌 **Interface Simples e Intuitiva:** Design focado na usabilidade, garantindo que a transcrição seja rápida e sem complicação.

## 🛠️ Tecnologias Utilizadas
| Componente        | Tecnologia                 |
|-------------------|----------------------------|
| **Frontend**      | React.js / Flutter         |
| **Backend**       | Node.js + Express          |
| **API de Áudio**  | Google Speech-to-Text API  |
| **Banco de Dados**| Firebase / PostgreSQL      |
| **Autenticação**  | Firebase Authentication    |

## 🏗️ Arquitetura do Sistema
```plaintext
🎤 Gravação de Áudio (App Web/Mobile)
   |
   🔗 API Backend (Node.js)
   |
   🛢️ Banco de Dados (Firestore/PostgreSQL)
   |
   🤖 Transcrição de Áudio (Google Speech API)
****
