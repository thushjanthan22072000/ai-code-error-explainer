const $ = (id) => document.getElementById(id);
const language = $("language"), code = $("code"), stdin = $("stdin");
let lastError = "";

const samples = {
 Python: 'print("Hello, World!")',
 JavaScript: 'console.log("Hello, World!");',
 TypeScript: 'const greeting: string = "Hello, World!";\\nconsole.log(greeting);',
 Java: 'public class Main {\\n  public static void main(String[] args) {\\n    System.out.println("Hello, World!");\\n  }\\n}',
 C: '#include <stdio.h>\\nint main() {\\n  printf("Hello, World!\\\\n");\\n  return 0;\\n}',
 "C++": '#include <iostream>\\nint main() {\\n  std::cout << "Hello, World!" << std::endl;\\n  return 0;\\n}',
 "C#": 'using System;\\nclass Program { static void Main() { Console.WriteLine("Hello, World!"); } }',
 Go: 'package main\\nimport "fmt"\\nfunc main() { fmt.Println("Hello, World!") }',
 Rust: 'fn main() { println!("Hello, World!"); }',
 PHP: '<?php echo "Hello, World!"; ?>',
 Ruby: 'puts "Hello, World!"',
 Kotlin: 'fun main() { println("Hello, World!") }',
 Swift: 'print("Hello, World!")',
 R: 'print("Hello, World!")',
 Perl: 'print "Hello, World!\\\\n";',
 Bash: 'echo "Hello, World!"',
 Lua: 'print("Hello, World!")',
 Dart: 'void main() { print("Hello, World!"); }'
};

$("sampleBtn").addEventListener("click", () => {
  code.value = samples[language.value] || 'print("Hello, World!")';
  stdin.value = "";
  $("output").textContent = "Sample loaded. Click Run Code.";
  $("runStatus").textContent = "Ready";
  $("message").textContent = "";
});
language.addEventListener("change", () => $("sampleBtn").click());

$("runBtn").addEventListener("click", async () => {
  $("message").textContent = "";
  $("runStatus").textContent = "Running…";
  $("output").textContent = "Executing your code. Please wait…";
  $("runBtn").disabled = true;
  try {
    const response = await fetch("/run", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({language:language.value, code:code.value, stdin:stdin.value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Execution failed.");
    const out = data.output || "(No output)";
    const err = data.stderr || "";
    $("output").textContent = out + (err ? "\\n\\nErrors / diagnostics:\\n" + err : "");
    $("runStatus").textContent = data.exitCode === 0 ? "Finished successfully" : `Finished (exit code: ${data.exitCode ?? "unknown"})`;
    lastError = err || (data.exitCode !== 0 ? out : "");
    if (lastError) {
      $("errorMessage").value = lastError;
      $("errorSection").hidden = false;
    }
  } catch (error) {
    $("output").textContent = "Execution could not be completed.";
    $("message").textContent = error.message;
    $("runStatus").textContent = "Failed";
  } finally {
    $("runBtn").disabled = false;
  }
});

$("explainBtn").addEventListener("click", () => {
  $("errorSection").hidden = false;
  if (lastError && !$("errorMessage").value) $("errorMessage").value = lastError;
  $("errorSection").scrollIntoView({behavior:"smooth", block:"start"});
});

$("analyzeBtn").addEventListener("click", async () => {
  const error = $("errorMessage").value.trim();
  if (!code.value.trim() || !error) {
    $("message").textContent = "Run code first or paste both code and an error message.";
    return;
  }
  $("analyzeBtn").disabled = true;
  $("explanation").textContent = "Gemini is preparing your explanation…";
  try {
    const response = await fetch("/analyze", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({language:language.value, code:code.value, error})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not explain the error.");
    $("explanation").textContent = data.explanation;
  } catch (error) {
    $("explanation").textContent = error.message;
  } finally {
    $("analyzeBtn").disabled = false;
  }
});
