// Export per-method CFG and data dependence (REACHING_DEF) graphs from a Joern CPG as JSON lines.
//
// Inputs (environment variables; `--param k=v` is unusable through Windows .bat launchers):
//   CG_CPG  path of the cpg.bin produced by joern-parse
//   CG_OUT  output .jsonl path
//
// Output records:
//   {"type":"file", "name": <file name as seen by Joern>}
//   {"type":"method", "name", "full_name", "signature", "filename", "namespace",
//    "type_decl", "line_start", "line_end", "modifiers": [...], "control": {TYPE: count},
//    "nodes": [{"id", "label", "line", "code"}],
//    "cfg_edges": [[src, dst]], "ddg_edges": [[src, dst, variable]]}
//
// Nodes = METHOD, METHOD_PARAMETER_IN, METHOD_RETURN and every CFG node of the method that has
// a CFG edge (Joern's structural BLOCK / CONTROL_STRUCTURE nodes without CFG edges are left
// out, as in `joern-export --repr cfg`). Edges are kept only when both ends are in that set.
import io.shiftleft.codepropertygraph.generated.EdgeTypes
import io.shiftleft.codepropertygraph.generated.nodes
import java.io.{BufferedWriter, FileWriter, PrintWriter}
import java.nio.charset.StandardCharsets

def esc(s: String): String = {
  val sb = new StringBuilder("\"")
  s.foreach {
    case '"'  => sb.append("\\\"")
    case '\\' => sb.append("\\\\")
    case '\n' => sb.append("\\n")
    case '\r' => sb.append("\\r")
    case '\t' => sb.append("\\t")
    case c if c < ' ' || c == '\u2028' || c == '\u2029' => sb.append("\\u%04x".format(c.toInt))
    case c    => sb.append(c)
  }
  sb.append("\"").toString
}
def optInt(o: Option[Int]): String = o.map(_.toString).getOrElse("null")
def strList(xs: Iterable[String]): String = xs.map(esc).mkString("[", ",", "]")

@main def exec() = {
  importCpg(sys.env("CG_CPG"))
  val out = new PrintWriter(new BufferedWriter(new FileWriter(sys.env("CG_OUT"), StandardCharsets.UTF_8)))
  cpg.file.name.l.distinct.foreach { f => out.println("{\"type\":\"file\",\"name\":" + esc(f) + "}") }
  var nMethods = 0
  cpg.method.isExternal(false).foreach { m =>
    val inner = m.cfgNode.filter(n => n._cfgIn.nonEmpty || n._cfgOut.nonEmpty).l
    val params = m.parameter.l
    val all = (List(m) ++ params ++ inner ++ List(m.methodReturn)).distinctBy(_.id)
    val ids = all.map(_.id).toSet
    val cfg = all.flatMap(n => n._cfgOut.map(d => (n.id, d.id))).filter(e => ids(e._2)).distinct
    val ddg = all.flatMap(n => n.outE(EdgeTypes.REACHING_DEF).map(e => (e.src.id, e.dst.id, String.valueOf(e.property))))
      .filter(e => ids(e._1) && ids(e._2)).distinct
    val control = m.controlStructure.filter(_.method.id == m.id).controlStructureType.l.groupBy(identity).map { case (k, v) => esc(k) + ":" + v.size }
    val nodeJson = all.map { n =>
      val (code, line) = n match {
        case c: nodes.Expression        => (c.code, c.lineNumber)
        case p: nodes.MethodParameterIn => (p.name, p.lineNumber)
        case r: nodes.MethodReturn      => ("RETURN", r.lineNumber)
        case mm: nodes.Method           => (mm.name, mm.lineNumber)
        case other                      => (other.label, None)
      }
      "{\"id\":" + n.id + ",\"label\":" + esc(n.label) + ",\"line\":" + optInt(line) +
        ",\"code\":" + esc(code.take(200)) + "}"
    }
    out.println(
      "{\"type\":\"method\",\"name\":" + esc(m.name) + ",\"full_name\":" + esc(m.fullName) +
      ",\"signature\":" + esc(m.signature) + ",\"filename\":" + esc(m.filename) +
      ",\"namespace\":" + esc(m.file.namespaceBlock.name.headOption.getOrElse("")) +
      ",\"type_decl\":" + esc(m.definingTypeDecl.fullName.headOption.getOrElse("")) +
      ",\"line_start\":" + optInt(m.lineNumber) + ",\"line_end\":" + optInt(m.lineNumberEnd) +
      ",\"modifiers\":" + strList(m.modifier.modifierType.l) +
      ",\"control\":{" + control.mkString(",") + "}" +
      ",\"nodes\":" + nodeJson.mkString("[", ",", "]") +
      ",\"cfg_edges\":" + cfg.map { case (a, b) => s"[$a,$b]" }.mkString("[", ",", "]") +
      ",\"ddg_edges\":" + ddg.map { case (a, b, v) => s"[$a,$b,${esc(v)}]" }.mkString("[", ",", "]") + "}")
    nMethods += 1
  }
  out.close()
  println(s"CG_EXPORT_DONE methods=$nMethods")
}
