#tested pass in linux
import langid

s1 = "今天是阳光明媚的一天。"
array = langid.classify(s1)
print('Chinese input, detected language:', array)

s2 = 'We are pleased to introduce today a new technology 每 Record Matching 每that automatically finds relevant historical records for every family tree on MyHerit'
array = langid.classify(s2)
print('English input, detected language:', array)

s3 = "你好"
array = langid.classify(s3)
print('Chinese input, detected language:', array)

s4 = "Lo más probable, a menos que haya demasiada distancia entre los candidatos, es que no se conozca al ganador de la elección la noche del martes 3. Algunos estados clave seguirán abriendo boletas enviadas previamente por varios días más. En ese marco, el presidente se ha negado a prometer una transición pacífica de poder, sujeta a lo que él considere una elección limpia."
array = langid.classify(s4)
print('spanish input, detected language:', array)

s5 = "Денег что, должно быть, даром переплатили, а мы-то им здесь верим, – язвительно заметил черномазый."
array = langid.classify(s5)
print('russian input, detected language:', array)

