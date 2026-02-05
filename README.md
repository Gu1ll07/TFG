[![TFG](https://search.brave.com/images?q=banner+coding&source=images)]
[![.NET](https://img.shields.io/badge/.NET-8.0%2C%209.0%2C%2010.0-512BD4)](https://docs.abblix.com/docs/technical-requirements)
[![language](https://img.shields.io/badge/language-C%23-239120)](https://learn.microsoft.com/ru-ru/dotnet/csharp/tour-of-csharp/overview)
[![OS](https://img.shields.io/badge/OS-linux%2C%20windows%2C%20macOS-0078D4)](https://docs.abblix.com/docs/technical-requirements)
[![CPU](https://img.shields.io/badge/CPU-x86%2C%20x64%2C%20ARM%2C%20ARM64-FF8C00)](https://docs.abblix.com/docs/technical-requirements)
[![security rating](https://sonarcloud.io/api/project_badges/measure?project=Abblix_Oidc.Server&metric=security_rating)](https://sonarcloud.io/summary/overall?id=Abblix_Oidc.Server)
[![reliability rating](https://sonarcloud.io/api/project_badges/measure?project=Abblix_Oidc.Server&metric=reliability_rating)](https://sonarcloud.io/summary/overall?id=Abblix_Oidc.Server)
[![maintainability rating](https://sonarcloud.io/api/project_badges/measure?project=Abblix_Oidc.Server&metric=sqale_rating)](https://sonarcloud.io/summary/overall?id=Abblix_Oidc.Server)
[![CodeQL analysis](https://github.com/Abblix/Oidc.Server/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Abblix/Oidc.Server/security/code-scanning?query=is%3Aopen)
[![tests](https://img.shields.io/badge/tests-2000+%20passing-brightgreen)](https://github.com/Abblix/Oidc.Server/tree/master/Abblix.Oidc.Server.UnitTests)
[![GitHub release](https://img.shields.io/github/v/release/Abblix/Oidc.Server)](#)
[![GitHub release date](https://img.shields.io/github/release-date/Abblix/Oidc.Server)](#)
[![GitHub last commit](https://img.shields.io/github/last-commit/Abblix/Oidc.Server)](#)
[![getting started](https://img.shields.io/badge/getting_started-guide-1D76DB)](https://docs.abblix.com/docs/getting-started-guide)
[![Free](https://img.shields.io/badge/free_for_non_commercial_use-brightgreen)](#-license)

⭐ Star us on GitHub — your support motivates us a lot! 🙏😊

🔥 Why TopoSoft is the best choice for topografic system   — find out in our [presentation](https://resources.abblix.com/pdf/abblix-oidc-server-presentation-eng.pdf) 📑

## Table of Contents
- [About](#-about)
- [What's New](#-whats-new)
- [Certification](#-certification)
- [How to Build](#-how-to-build)
- [Documentation](#-documentation)
- [Feedback and Contributions](#-feedback-and-contributions)
- [License](#-license)
- [Contacts](#%EF%B8%8F-contacts)

## 🚀 About

**Abblix OIDC Server** is a .NET library designed to provide comprehensive support for OAuth2 and OpenID Connect on the server side. It adheres to high standards of flexibility, reusability, and reliability, utilizing well-known software design patterns, including modular and hexagonal architectures. These patterns ensure the following benefits:

- **Modularity**: Different parts of the library can function independently, enhancing the library's modularity and allowing for easier maintenance and updates.
- **Testability**: Improved separation of concerns makes the code more testable.
- **Maintainability**: Clear structure and separation facilitate better management of the codebase.

The library also supports Dependency Injection through the standard .NET DI container, aiding in the organization and management of code. Specifically tailored for seamless integration with ASP.NET WebApi, Abblix OIDC Server employs standard controller classes, binding, and routing mechanisms, simplifying the integration of OpenID Connect into your services.

## ✨ What's New

### Version 2.0.0 (Latest)

⚡ **Breaking Changes**
- **Result Pattern Migration**: Migrated to `Result<TSuccess, TFailure>` pattern for compiler-enforced explicit error handling and functional programming style
- **Framework Updates**: Dropped .NET 6 & 7 (EOL) - now targets .NET 8 (LTS), .NET 9 (STS), and .NET 10 (LTS - released Nov 2025, supported until Nov 2028)

🚀 **Features**
- **mTLS Client Authentication (RFC 8705)**: Self-signed and PKI/CA validation with certificate-bound tokens
- **JWT Bearer Grant Type (RFC 7523)**: Service-to-service authentication using signed JWTs for secure API-to-API communication
- **Device Authorization Grant (RFC 8628)**: OAuth flow for input-constrained devices (smart TVs, IoT, CLI tools)
- **CIBA Ping/Push Modes & Long-Polling**: Complete delivery mode implementation with ping notifications, push token delivery, and long-polling support
- **client_secret_jwt Authentication**: JWT-based client authentication per OIDC Core spec
- **SSRF Protection**: Multi-layered defense with DNS validation and IP blocking
- **Protocol Buffer Serialization**: 40-60% smaller storage footprint with faster processing
- **ECDSA Certificate Support**: Enables compliance with modern security standards that mandate or prefer elliptic curve cryptography

> **Migration Note**: This release contains breaking changes. See 📋[Migration Guide](MIGRATION-2.0.md).

[Back to top](#top)

## 📝 How to Start the APP TFG 1

To build the packages, follow these steps:

```shell
# Open a terminal (Command Prompt or PowerShell for Windows, Terminal for macOS or Linux)

# Ensure Git is installed
# Visit https://git-scm.com to download and install console Git if not already installed

# Clone the repository
git clone https://github.com/Abblix/Oidc.Server.git

# Navigate to the project directory
cd Oidc.Server

# Check if .NET SDK is installed
dotnet --version  # Check the installed version of .NET SDK
# Visit the official Microsoft website to install or update it if necessary

# Restore dependencies
dotnet restore

# Compile the project
dotnet build

```

## 📝 How to Start the APP TFG 2

To build the packages, follow these steps:

```shell
# Open a terminal (Command Prompt or PowerShell for Windows, Terminal for macOS or Linux)

# Ensure Git is installed
# Visit https://git-scm.com to download and install console Git if not already installed

# Clone the repository
git clone https://github.com/Abblix/Oidc.Server.git

# Navigate to the project directory
cd Oidc.Server

# Check if .NET SDK is installed
dotnet --version  # Check the installed version of .NET SDK
# Visit the official Microsoft website to install or update it if necessary

# Restore dependencies
dotnet restore

# Compile the project
dotnet build

```
                                                                                                                                                                            
## 📚 Documentation

### Getting Started
Explore the [Getting Started Guide](https://docs.abblix.com/docs/getting-started-guide).
In this guide, you will create a working solution step by step, building an OpenID Connect Provider using ASP.NET MVC and the Abblix OIDC Server solution.

To better understand the Abblix OIDC Server product, we recommend visiting our [Documentation](https://docs.abblix.com/docs) site. There, you will find useful information about the product and the OpenID Connect standard.

[Back to top](#top)

## 🗨️ Contacts

For more details about the project or any information regarding this repository, feel free to reach out to me. I'm  here to provide support and answer any questions you may have. Below are the best ways to contact:

- **Email**: Send us your inquiries or support requests at [guillobermejo@abblix.com](mailto:guillobermejo@gmail.com).

Check my LinkedIn profile:

<a href="https://www.linkedin.com/in/juan-guillo-bermejo-a5b940205/" target="_blank">
  <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" width="30" />
</a>


We look forward to assisting you and ensuring your experience with our products is successful and enjoyable!

[Back to top](#top)
