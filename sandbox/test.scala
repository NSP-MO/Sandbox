import scala.io.StdIn.readLine

object Main {
    def main(args: Array[String]): Unit = {

        val n = scala.io.StdIn.readInt()

        val a = readLine().split(" ").map(_.toInt)

        val min = a.min
        val max = a.max

        val odd = a.count(_ % 2 != 0)

        println(s"$min $max $odd")
    }
}