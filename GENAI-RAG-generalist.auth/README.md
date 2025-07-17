<h1 align="center">
   <a href="#"> Sentinel Keycloak Docker Documentation </a><br />
   <small>(Keycloak)</small>
</h1>

<h3 align="center">
    This documentation provides instructions for running Keycloak in a Docker container for the Neuai Sentinel project, based on the <a href="https://dev.azure.com/radixeng/AKL-2023-001-23001-MonitoramentoDeAtivos/_git/doc?version=GBmaster&path=/02.Analise/arquitetura/AKL-2023-001-23001-SFT-001-ArquiteturaSistema.docx">Architecture Documentation</a>. It utilizes the official Keycloak Docker image and provides steps for configuration and usage.
</h3>

</p>

<h4 align="center">
    Status: In Progress
</h4>

<p align="center">
 <a href="#about">About</a> •
 <a href="#how-it-works">How it works</a> •
 <a href="#tech-stack">Tech Stack</a>


## About

The Neuai Sentinel project utilizes Keycloak, an open-source identity and access management solution, for authentication and authorization. This documentation provides instructions for running Keycloak in a Docker container.

<div align="center">
<img src="template-theme/login/resources/img/keycloak-logo-text.png" />
</div>

## How it works

### Install and Run
1. Install Docker: https://docs.docker.com/engine/install/
1. Pull the dependency images Docker image: `docker compose pull`
1. Build the compose image: `docker compose build`
1. Run the Keycloak container: `docker compose up`
1. Access Keycloak admin console: `http://localhost:8080/admin`
1. To view the login page: `http://localhost:8080/admin/template/console/`
1. Configure Keycloak according to your project's requirements.

**⚠️IMPORTANT:** after doing changes in Admin UI, export the import json and overwrite the `realm-import-dev-env/realm-template.json` file.

**⚠️⚠️IMPORTANT:** Any changes on local docker Admin UI don't reflect on cloud environment, you need to redo the configuration.

### Customize
According to the documentation at [Keycloak Themes](https://www.keycloak.org/docs/latest/server_development/#_themes), customization should be done in the `template-theme` folder following the steps provided in the link.

- To customize the CSS, edit the `template-theme/login/resources/css/styles.css` file.
- To customize the JavaScript, edit the `template-theme/login/resources/js/script.js` file.
- To customize the page layout using [FreeMarker template](https://freemarker.apache.org/) that generates the final HTML, edit the `template-theme/login/login.ftl` file.

All changes will be automatically reflected in the Docker without the need for rebuild or new execution.

## Tech Stack
- [Keycloak](https://www.keycloak.org/)
- [Docker](https://www.docker.com/)
