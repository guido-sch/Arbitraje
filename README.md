
<h1 align="left"> Arbitraje </h1>
El objetivo del bot es poder calcular tasas implícitas y obtener oportunidades de arbitraje de tasa entre diferentes instrumentos (GALICIA, YPF, PAMPA y DOLAR). Para ello, se escribió en Python un script que se conecta por Websocket a Remarket para obtener los valores Futuros y por yfinance se obtiene el spot de los instrumentos. La ventaja de Websocket, es que es bidireccional y asincrónico, por lo tanto, no se tiene que hacer querys continuamente. Una vez subscrito a los instrumentos, cuando haya algún cambio en los valores, se envía automaticamente la información actualizada. Con la informacion actualizada, se calculan las tasas implícitas (bid y offer) para cada instrumento. Por último, se comparan las tasas implícitas offer (donde uno se fondea) con la bid (donde uno coloca). Si este spread es positivo, hay oportunidad de arbitraje. Se busca cuál es el mayor spread y se plantea la mejor estrategia de arbitraje.


<h2 align="left"> Arbitraje de tasa </h2>
El arbitraje de tasa consiste en fondearte (hacer plata) a una tasa baja, y colocar el dinero abriendo una posición futura. En un fondeo, se està en una posición corta (short selling) con una acción y posición larga (long) en futuro. En una colocación, se hace lo opuesto, se está en long en la acción y short en el futuro. Si la diferencia de tasas es positiva (tasa colocar - tasa fondear), hay una oportunidad de arbitraje.


<h4 align="left"> Ejemplo </h4>
Supongamos que la acción de YPF sale 10$ y el futuro 11$. Si vendo una acción y compro un futuro de YPF, con esta operación me estoy fondeando al 10%.
Si en Galicia hago la operación opuesta, cuyo spot es de 10$ y su futuro de 12$, estoy ganando 20%. Por lo tanto la estrategia seria fondear en YPF y colocar en Galicia, ya que la tasa de YPF es más baja que la de Galicia. Cabe aclarar que la tasa que uno compara es la OFFER para fondearte con la BID para colocar.


<h4 align="left"> Cálculo de tasas implícitas </h4>
Para calcular las tasas implícitas, se necesitan los precio spot del underlying, bid y offer del futuro y la maturity del futuro. El spot se obtiene de yfinance mientras que los valores del futuro de remarket. El mismo remarket da el maturity del producto. Para calcular la tasa implícita, se usa la fórmula de Tasa Implícita Anualizada (TNA), cuya fórmula es la siguiente: 

$$\text{TNA}=\left(\frac{\text{Precio futuro}}{\text{Precio spot}} - 1 \right) \left( \frac{365}{\text{dias de vencimiento}} \right)$$

La ventaja de la TNA es que la mayor cantidad de tasas en la economía se calculan de esta forma.


<h2 align="left"> Código de python </h2>

Una vez creado un usuario en https://remarkets.primary.ventures/ se puede instalar el paquete pyRofex en python (pip install pyRofex), y obtener los valores futures de remarkets. Con yfinance (pip install yfinance), se pueden obtener los valores spot de los underlying.

El código de python (arbitraje_tasas.py) calcula cuál es la mejor estrategia entre los instrumentos (GALICIA, YPF, PAMPA y DOLAR). El mismo realiza los siguientes pasos

1. Importa librerías necesarias, define variables y funciones que se van a utilizar (función para tomar el spot de yfinance, cálculo de TNA, unit test)
2. Inicializa el entorno en REMARKET, con los datos de usuario contraseña del mismo.
3. Se define la función handler, la cual va a recibir la información por websocket, y va a calcular las tasas implícitas y oportunidad de arbitraje.
4. Inicialización de la conexión por Websocket.
5. Subscripción para recibir la información de mercado.
