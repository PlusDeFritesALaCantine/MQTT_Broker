# Brocker MQTT

Getting started README for the **Brocker MQTT** project.

## Objective

This project provides a foundation to run and test an MQTT broker locally, making MQTT client development and integration easier.

## Prerequisites

- Windows, Linux, or macOS
- A terminal (PowerShell, CMD, Bash)
- An MQTT client for testing (EMQX MQTTX Web view)

## Quick Start

1. **Clone the repository**

	```bash
	git clone <repository-url>
	cd brocker-mqtt
	```

2. **Install dependencies**

	Follow the instructions for the language/framework used in the project.

3. **Start the broker**

	Run the startup command provided by the project.

4. **Verify it works**

	In a first terminal, subscribe to a topic:

	```bash
	mqttx sub -h localhost -p 1883 -t test/topic
	```

	In a second terminal, publish a message:

	```bash
	mqttx pub -h localhost -p 1883 -t test/topic -m "hello"
	```

	If the message is received, the broker is working correctly.

## Recommended Project Structure

- `src/`: main source code
- `config/`: configuration files
- `scripts/`: execution and automation scripts
- `tests/`: unit and integration tests

## Configuration

Common settings to verify:

- MQTT port (default `1883`)
- Authentication (enabled/disabled)
- TLS/SSL configuration if needed
- Message and session persistence

## Development Best Practices

- Version only sample configurations
- Do not commit secrets
- Add tests for critical publish/subscribe scenarios
- Document every configuration change that impacts runtime behavior

## Quick Troubleshooting

- **Port already in use**: change the service port or stop the conflicting process.
- **Connection refused**: verify host, port, and firewall rules.
- **No message received**: validate topic, QoS, and access permissions.

## Contribution

1. Create a working branch
2. Implement changes
3. Add/update tests
4. Open a pull request with a clear description

## License

Specify the project license here (e.g., MIT, Apache-2.0, proprietary).
