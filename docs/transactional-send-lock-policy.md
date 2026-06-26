# Transactional Send Lock Policy

Send queue items are claimed before provider calls. Only `READY_TO_SEND_CONTROLLED` items can be claimed. Claimed items move to `SENDING`.

Locks prevent concurrent sends of the same queue item.
