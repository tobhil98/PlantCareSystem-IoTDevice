## Obedient Fighting Snakes - SelfFlowers
[Toby Hillier](https://github.com/tobhil98), [Andrzej Kowalewski](https://github.com/akowal3), [Oliver Stiff](https://github.com/ostiff)

#### [Marketing website](https://co333robotics.wixsite.com/embedded)

The diagram below presents a high level overview of our SelfFlower system with protocols used for communication between components

![HL overview](/es_diagram.jpg)


#### [Server code](./proxy):
- [Powerapps](https://apps.powerapps.com/play/42d01a4a-176c-4679-bb07-0f85b2069cdd?tenantId=2b897507-ee8c-4575-830b-4f8267c3d307&source=portal&screenColor=rgba(0%2C%20176%2C%20240%2C%201)) implements a fronted, which allows users to change the settings of the IoT device, as well as view real-time and historical data
- [Google Sheets](./database) implements the backend component because of its availability and ease of access using Python APIs
- [Server Proxy](./proxy/proxy.py) running on another Raspberry Pi acts as a proxy between the IoT device and the database
- [Amazon Alexa](./alexa) is used as another mean for the user to interacting with the IoT device, which allows to change state of the device and obtain latest updates.

#### [Client Code](./client)
