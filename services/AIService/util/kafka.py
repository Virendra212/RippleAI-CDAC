from util.kafka import KafkaProducer

HOST = "kafka-2fbe3dc4-shakyashivam236-581e.l.aivencloud.com"
SSL_PORT = 11409
TOPIC = "demo-topic"

producer = KafkaProducer(
    bootstrap_servers=f"{HOST}:{SSL_PORT}",
    security_protocol="SSL",
    ssl_cafile="ca.pem",
    ssl_certfile="service.cert",
    ssl_keyfile="service.key",
)