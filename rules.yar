rule SuspiciousEval {
    strings:
        $eval = "eval("
    condition:
        $eval
}
