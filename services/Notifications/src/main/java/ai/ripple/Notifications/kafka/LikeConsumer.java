package ai.ripple.Notifications.kafka;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
@Slf4j
@RequiredArgsConstructor
public class LikeConsumer {

    @KafkaListener(topics = "post-engagement-events", groupId = "notification-service")
    public void consume(String message) {
        try {
            log.info("Received Kafka message in Notification Service for likes and comments: {}", message);

            //push notifications
            


        } catch (Exception e) {
            log.error("Error processing Kafka message in Notification Service: {}", message, e);
        }
    }
}
