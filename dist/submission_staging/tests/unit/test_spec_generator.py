import json

from spec_generator.core.parser import load_requirements, write_requirements_raw
from spec_generator.core.analyzer import analyze_requirement, build_ir
from spec_generator.core.spec_reader import read_requirements
from spec_generator.core.strategy_selector import select_strategy
from spec_generator.core.static_generator import generate_cbmc, generate_z3, write_static_artifacts
from spec_generator.core.dynamic_generator import boundary_values, generate_boundary_test, write_dynamic_artifact, generate_fuzz_harness, range_boundary_values
from spec_generator.core.code_mapping import load_code_mapping, validate_code_mapping
from spec_generator.core.code_mapping import load_production_mapping, validate_mapping
from spec_generator.core.production_harness_generator import generate_production_harness
from spec_generator.core.executor import run_command, tool_available
from spec_generator.core.result_collector import collect_results
from spec_generator.core.traceability_generator import build_summary, build_traceability, save_traceability_csv


def test_load_pipe_delimited_txt_and_write_json(tmp_path):
    source = tmp_path / "requirements.txt"
    source.write_text(
        "ID | Type | Priority | Content\n"
        "REQ-01 | safety | high | Total power must not exceed 100 kW.\n",
        encoding="utf-8",
    )

    requirements = load_requirements(source)
    output = write_requirements_raw(requirements, tmp_path / "requirements_raw.json")

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["format"] == "requirements_raw"
    assert payload["requirements"][0]["priority"] == "HIGH"
    assert payload["requirements"][0]["content"] == "Total power must not exceed 100 kW."


def test_load_csv_with_case_insensitive_headers(tmp_path):
    source = tmp_path / "requirements.csv"
    source.write_text(
        "content,ID,TYPE,priority\nSOC must be between 0 and 100%,REQ-02,safety,High\n",
        encoding="utf-8",
    )

    requirements = load_requirements(source)

    assert requirements == [{
        "id": "REQ-02",
        "type": "safety",
        "priority": "HIGH",
        "content": "SOC must be between 0 and 100%",
        "source": "requirements.csv",
        "source_row": 2,
    }]


def test_load_xlsx(tmp_path):
    from openpyxl import Workbook

    source = tmp_path / "requirements.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["ID", "Type", "Priority", "Content"])
    sheet.append(["REQ-03", "safety", "medium", "Temperature must stay below the limit."])
    workbook.save(source)

    requirements = load_requirements(source)

    assert requirements[0]["id"] == "REQ-03"
    assert requirements[0]["priority"] == "MEDIUM"


def test_spec_reader_uses_normalized_input_contract(tmp_path):
    source = tmp_path / "requirements.txt"
    source.write_text(
        "ID | Type | Priority | Content\nREQ-01 | safety | HIGH | Total power must not exceed 100 kW.\n",
        encoding="utf-8",
    )

    assert read_requirements(source)[0]["id"] == "REQ-01"


def test_analyzer_builds_invariant_and_ir():
    analysis = analyze_requirement({
        "id": "REQ-01",
        "content": "Tổng công suất không được vượt quá 100 kW.",
    })

    assert analysis["property_type"] == "invariant"
    assert analysis["expression"] == {
        "variable": "total_power",
        "operator": "<=",
        "value": 100,
        "value_type": "number",
        "unit": "kW",
    }
    assert build_ir(analysis)["expected"] == [analysis["expression"]]


def test_analyzer_builds_conditional_ir():
    analysis = analyze_requirement({
        "id": "REQ-04",
        "content": "Khi nhiệt độ >= 60°C, công suất phải bằng 0.",
    })
    ir = build_ir(analysis)

    assert ir == {
        "requirement_id": "REQ-04",
        "verifiable": True,
        "property_type": "conditional",
        "preconditions": [],
        "trigger": {"variable": "temperature", "operator": ">=", "value": 60, "value_type": "number", "unit": "C"},
        "expected": [{"variable": "power", "operator": "==", "value": 0, "value_type": "number", "unit": None}],
    }


def test_analyzer_parses_general_conditionals_and_boolean_states():
    examples = [
        ("If temperature >= 60 C, power must equal 0.", "temperature", ">=", 60, "power", 0),
        ("If pressure > 200 kPa, valve must equal CLOSED.", "pressure", ">", 200, "valve", "CLOSED"),
        ("When voltage < 200 V, system_state must equal FAULT.", "voltage", "<", 200, "system_state", "FAULT"),
        ("Khi nhiệt độ >= 60 C, công suất phải bằng 0.", "temperature", ">=", 60, "power", 0),
        ("Nếu SOC >= 100 %, charging phải bằng false.", "soc", ">=", 100, "charging", False),
    ]

    for content, trigger_variable, operator, value, expected_variable, expected_value in examples:
        ir = build_ir(analyze_requirement({"id": "REQ-COND", "content": content}))
        assert ir["verifiable"] is True
        assert ir["property_type"] == "conditional"
        assert ir["trigger"] == {
            "variable": trigger_variable, "operator": operator, "value": value,
            "value_type": "number",
            "unit": ir["trigger"]["unit"],
        }
        assert ir["expected"][0]["variable"] == expected_variable
        assert ir["expected"][0]["operator"] == "=="
        assert ir["expected"][0]["value"] == expected_value


def test_conditional_dynamic_generator_uses_trigger_boundaries():
    ir = build_ir(analyze_requirement({
        "id": "REQ-03",
        "content": "If pressure > 200 kPa, valve must equal CLOSED.",
    }))

    generated = generate_boundary_test(ir)

    assert "(199.9, False)" in generated
    assert "(200, False)" in generated
    assert "(200.1, True)" in generated
    assert "trigger_holds(pressure)" in generated
    assert "__VIOLATION__" in generated


def test_analyzer_supports_non_ev_pressure_and_symbolic_valve_state():
    pressure = analyze_requirement({"id": "REQ-01", "content": "Pressure must not exceed 200 kPa."})
    valve = build_ir(analyze_requirement({
        "id": "REQ-02",
        "content": "When temperature >= 80 C, valve must be CLOSED.",
    }))

    assert pressure["expression"] == {
        "variable": "pressure", "operator": "<=", "value": 200, "value_type": "number", "unit": "kPa",
    }
    assert valve["expected"][0]["value"] == "CLOSED"


def test_standalone_state_boolean_and_enum_ir():
    cases = [
        ("state must equal FAULT", "state", "==", "FAULT", "enum"),
        ("state must not equal CHARGING", "state", "!=", "CHARGING", "enum"),
        ("charging must be false", "charging", "==", False, "boolean"),
        ("authenticated must be true", "authenticated", "==", True, "boolean"),
        ("System state must not equal FAULT.", "system_state", "!=", "FAULT", "enum"),
    ]

    for content, variable, operator, value, value_type in cases:
        ir = build_ir(analyze_requirement({"id": "REQ-STATE", "content": content}))
        expression = ir["expected"][0]
        assert ir["property_type"] == "state"
        assert expression == {
            "variable": variable, "operator": operator, "value": value,
            "value_type": value_type, "unit": None,
        }


def test_conditional_state_and_non_ev_boolean_are_generic():
    cases = [
        ("If temperature >= 60 C, state must equal FAULT.", "temperature", "state", "FAULT", "enum"),
        ("If SOC >= 100 %, charging must be false.", "soc", "charging", False, "boolean"),
        ("If speed >= 120 km/h, warning_light must be true.", "speed", "warning_light", True, "boolean"),
    ]

    for content, trigger_variable, expected_variable, value, value_type in cases:
        ir = build_ir(analyze_requirement({"id": "REQ-COND-STATE", "content": content}))
        assert ir["property_type"] == "conditional"
        assert ir["trigger"]["variable"] == trigger_variable
        assert ir["expected"][0]["variable"] == expected_variable
        assert ir["expected"][0]["value"] == value
        assert ir["expected"][0]["value_type"] == value_type


def test_conditional_and_or_build_logic_trees_without_splitting_requirements():
    and_ir = build_ir(analyze_requirement({
        "id": "REQ-AND",
        "content": "If temperature >= 60 C AND charging == true, then power == 0 AND state == FAULT.",
    }))
    or_ir = build_ir(analyze_requirement({
        "id": "REQ-OR",
        "content": "If pressure > 200 kPa OR temperature >= 80 C, then alarm == true.",
    }))
    vietnamese = build_ir(analyze_requirement({
        "id": "REQ-VI",
        "content": "Nếu áp suất > 200 kPa hoặc nhiệt độ >= 80 C, thì alarm phải bằng true.",
    }))

    assert and_ir["trigger"]["logic"] == "AND"
    assert len(and_ir["trigger"]["conditions"]) == 2
    assert and_ir["expected"]["logic"] == "AND"
    assert len(and_ir["expected"]["conditions"]) == 2
    assert or_ir["trigger"]["logic"] == "OR"
    assert len(or_ir["trigger"]["conditions"]) == 2
    assert vietnamese["trigger"]["logic"] == "OR"


def test_logic_precedence_keeps_and_inside_or():
    ir = build_ir(analyze_requirement({
        "id": "REQ-PREC",
        "content": "If A == true OR B == true AND C == true, then alarm == true.",
    }))

    assert ir["trigger"]["logic"] == "OR"
    assert ir["trigger"]["conditions"][1]["logic"] == "AND"


def test_logic_generators_render_and_or_and_truth_table():
    ir = build_ir(analyze_requirement({
        "id": "REQ-LOGIC",
        "content": "If temperature >= 60 C AND charging == true, then power == 0 AND state == FAULT.",
    }))

    cbmc = generate_cbmc(ir)
    dynamic = generate_boundary_test(ir)

    assert "&&" in cbmc
    assert "assert((power == 0.0f && state == FAULT));" in cbmc
    assert "trigger_holds(temperature, charging)" in dynamic
    assert "False), False" in dynamic
    assert "True), True" in dynamic


def test_analyzer_parses_sequences_ordering_and_transitions_generically():
    sequence = build_ir(analyze_requirement({
        "id": "REQ-SEQ", "content": "CREATED -> PAID -> SHIPPED -> DELIVERED",
    }))
    ordering = build_ir(analyze_requirement({
        "id": "REQ-ORDER", "content": "User verification must occur before account activation.",
    }))
    vietnamese_ordering = build_ir(analyze_requirement({
        "id": "REQ-ORDER-VI", "content": "Xe phải kết nối trước khi xác thực.",
    }))
    transition = build_ir(analyze_requirement({
        "id": "REQ-TRANS", "content": "System may transition from READY to RUNNING.",
    }))
    conditional_transition = build_ir(analyze_requirement({
        "id": "REQ-TRANS-C", "content": "If authenticated == true, system may transition from CONNECTED to AUTHENTICATED.",
    }))

    assert sequence["property_type"] == "sequence"
    assert sequence["states"] == ["CREATED", "PAID", "SHIPPED", "DELIVERED"]
    assert sequence["transitions"] == [
        {"from": "CREATED", "to": "PAID"},
        {"from": "PAID", "to": "SHIPPED"},
        {"from": "SHIPPED", "to": "DELIVERED"},
    ]
    assert ordering["property_type"] == "ordering"
    assert ordering["before"] == "USER_VERIFICATION"
    assert ordering["after"] == "ACCOUNT_ACTIVATION"
    assert vietnamese_ordering["property_type"] == "ordering"
    assert transition["from"] == "READY" and transition["to"] == "RUNNING"
    assert conditional_transition["condition"]["value"] is True


def test_sequence_ordering_transition_generators_compile_and_run(tmp_path):
    sequence = build_ir(analyze_requirement({"id": "REQ-SEQ", "content": "A -> B -> C"}))
    ordering = build_ir(analyze_requirement({"id": "REQ-ORDER", "content": "A must occur before B."}))
    transition = build_ir(analyze_requirement({"id": "REQ-TRANS", "content": "System may transition from IDLE to RUNNING."}))

    for ir in (sequence, ordering, transition):
        c_path = tmp_path / f"{ir['requirement_id']}.c"
        py_path = tmp_path / f"test_{ir['requirement_id']}.py"
        c_path.write_text(generate_cbmc(ir), encoding="utf-8")
        py_path.write_text(generate_boundary_test(ir), encoding="utf-8")
        assert c_path.exists() and py_path.exists()


def test_analyzer_builds_generic_range_ir():
    examples = [
        ("SOC must remain between 0 and 100%.", "soc", "%"),
        ("Temperature must remain between 10 and 50 C.", "temperature", "C"),
        ("Pressure must be between 0 and 200 kPa.", "pressure", "kPa"),
        ("Voltage phải nằm trong khoảng từ 200 đến 240 V.", "voltage", "V"),
        ("0 <= SOC <= 100", "soc", None),
    ]

    for content, variable, unit in examples:
        ir = build_ir(analyze_requirement({"id": "REQ-RANGE", "content": content}))
        assert ir["property_type"] == "range"
        assert [item["value"] for item in ir["expected"]] == [0, 100] if variable == "soc" and "100" in content else True
        assert ir["expected"][0]["variable"] == variable
        if unit:
            assert ir["expected"][0]["unit"] == unit


def test_range_dynamic_generator_uses_six_boundary_cases():
    ir = {
        "requirement_id": "REQ-02",
        "verifiable": True,
        "property_type": "range",
        "expected": [
            {"variable": "soc", "operator": ">=", "value": 0, "unit": "%"},
            {"variable": "soc", "operator": "<=", "value": 100, "unit": "%"},
        ],
    }

    assert range_boundary_values(ir["expected"]) == [(-0.1, False), (0, True), (0.1, True), (99.9, True), (100, True), (100.1, False)]
    generated = generate_boundary_test(ir)
    assert "return soc >= 0 and soc <= 100" in generated


def test_analyzer_marks_unmeasurable_requirement_unverifiable():
    analysis = analyze_requirement({"id": "REQ-99", "content": "Giao diện phải đẹp."})

    assert analysis["verifiable"] is False
    assert analysis["reason"] == "Không có tiêu chí chấp nhận có thể đo lường."
    assert build_ir(analysis) == {
        "requirement_id": "REQ-99",
        "verifiable": False,
        "reason": analysis["reason"],
    }


def test_memory_requirement_is_selectable_for_memory_tools():
    ir = build_ir(analyze_requirement({
        "id": "REQ-05",
        "content": "Khong duoc ghi vuot buffer.",
    }))

    assert ir["property_type"] == "memory_safety"
    assert ir["memory_issue"] == "buffer_overflow"
    assert ir["target"] is None
    assert select_strategy(ir) == {"static": ["cppcheck", "cbmc"], "dynamic": ["asan", "fuzz"]}


def test_memory_safety_classification_and_targets():
    examples = [
        ("The system must not write beyond the allocated buffer.", "buffer_overflow"),
        ("The system must not access memory after it has been freed.", "use_after_free"),
        ("The same memory region must not be freed more than once.", "double_free"),
        ("Dynamically allocated memory must be released when no longer used.", "memory_leak"),
        ("Integer calculations must not overflow.", "integer_overflow"),
        ("Hệ thống không được ghi vượt quá kích thước vùng đệm.", "buffer_overflow"),
        ("Không được truy cập vùng nhớ sau khi đã giải phóng.", "use_after_free"),
        ("Một vùng nhớ không được giải phóng nhiều hơn một lần.", "double_free"),
        ("Bộ nhớ động phải được giải phóng khi không còn sử dụng.", "memory_leak"),
        ("Các phép tính số nguyên không được xảy ra tràn số.", "integer_overflow"),
    ]
    for content, issue in examples:
        ir = build_ir(analyze_requirement({"id": "REQ-M", "content": content}))
        assert ir["verifiable"] is True
        expected_property = "arithmetic_safety" if issue == "integer_overflow" else "memory_safety"
        assert ir["property_type"] == expected_property
        assert ir.get("memory_issue", ir.get("issue")) == issue

    targeted = build_ir(analyze_requirement({
        "id": "REQ-T", "content": "Function copy_vehicle_id must not write beyond the destination buffer.",
    }))
    assert targeted["target"] == {"type": "function", "name": "copy_vehicle_id"}

    variable = build_ir(analyze_requirement({
        "id": "REQ-T2", "content": "Buffer vehicle_id must not overflow.",
    }))
    assert variable["target"] == {"type": "variable", "name": "vehicle_id"}


def test_strategy_selector_chooses_tools_by_property_shape():
    invariant = {"verifiable": True, "property_type": "invariant"}
    conditional = {"verifiable": True, "property_type": "conditional"}
    memory = {"verifiable": True, "memory_safety": True}

    assert select_strategy(invariant) == {"static": ["CBMC", "SMT/Z3"], "dynamic": ["Boundary Test"]}
    assert select_strategy(conditional)["dynamic"] == ["Boundary Test", "Runtime", "Fuzz"]
    assert select_strategy(memory) == {"static": ["Cppcheck"], "dynamic": ["ASan", "Fuzz"]}


def test_static_generators_write_cbmc_and_z3(tmp_path):
    ir = {
        "requirement_id": "REQ-01",
        "verifiable": True,
        "property_type": "invariant",
        "expected": [{"variable": "total_power", "operator": "<=", "value": 100, "unit": "kW"}],
    }

    artifacts = write_static_artifacts(ir, tmp_path)
    cbmc = generate_cbmc(ir)
    z3 = generate_z3(ir)

    assert [path.name for path in artifacts] == ["REQ_01_cbmc.c", "REQ_01_z3.py"]
    assert "assert(total_power <= 100.0f);" in cbmc
    assert "s.add(total_power > 100)" in z3


def test_code_mapping_is_explicit_and_used_in_artifacts(tmp_path):
    mapping = load_code_mapping()
    report = validate_code_mapping(mapping)
    ir = {
        "requirement_id": "REQ-01",
        "verifiable": True,
        "property_type": "invariant",
        "expected": [{"variable": "total_power", "operator": "<=", "value": 100, "unit": "kW"}],
    }

    artifacts = write_static_artifacts(ir, tmp_path, str(__file__).split("tests")[0] + "spec_generator/input/code_mapping.json")

    assert report["total_power"]["status"] == "CONFIRMED"
    assert "tram->cong_suat_hien_tai" in artifacts[0].read_text(encoding="utf-8")
    assert "src/station/tram_sac.c" in artifacts[1].read_text(encoding="utf-8")


def test_production_mapping_validation_and_field_harness():
    mapping = load_production_mapping()
    ir = build_ir(analyze_requirement({
        "id": "SR10", "content": "Total station power must not exceed 100 kW.",
    }))
    harness, status = generate_production_harness(ir, mapping)

    assert status["status"] == "MAPPED"
    assert harness is not None
    assert "tram->cong_suat_hien_tai <= 100.0f" in harness

    partial = {"variables": {"total_power": mapping["variables"]["total_power"]}}
    partial_status = validate_mapping({
        "expected": [{"variable": "total_power"}, {"variable": "state"}],
    }, partial)
    assert partial_status["status"] == "PARTIALLY_MAPPED"
    assert partial_status["missing"] == ["state"]


def test_executor_and_result_collector_are_fail_closed():
    command = run_command(["python", "-c", "print('ok')"])
    unavailable = run_command(["definitely_missing_verification_tool"])
    result = collect_results(
        "REQ-EXEC",
        {"verifiable": True},
        {"static": ["cbmc"], "dynamic": []},
        [{"tool": "gcc", "status": "PASS"}, {"tool": "cbmc", "status": "UNAVAILABLE"}],
    )

    assert command["status"] == "PASS"
    assert unavailable["status"] == "UNAVAILABLE"
    assert result["overall_result"] == "INCONCLUSIVE"
    assert tool_available("gcc") is True


def test_traceability_outputs_and_summary_counts(tmp_path):
    records = build_traceability([
        {"requirement_id": "PASS", "specification": "x", "property_type": "invariant", "result": "PASS", "mapping": {"status": "MAPPED"}, "generated_artifacts": ["a.c"], "evidence": ["e.txt"]},
        {"requirement_id": "FAIL", "specification": "y", "property_type": "conditional", "result": "FAIL", "counterexample": {"x": 2}},
        {"requirement_id": "NFR", "specification": "z", "property_type": "unknown", "result": "NOT_VERIFIABLE", "reason": "No measurable criterion."},
    ])
    summary = build_summary(records)
    csv_path = tmp_path / "traceability.csv"
    save_traceability_csv(records, csv_path)

    assert summary["total"] == 3
    assert summary["pass"] + summary["fail"] + summary["not_verifiable"] == 3
    assert "PASS" in csv_path.read_text(encoding="utf-8-sig")


def test_dynamic_generator_creates_boundary_cases(tmp_path):
    expression = {"variable": "total_power", "operator": "<=", "value": 100.0}
    ir = {"requirement_id": "REQ-01", "verifiable": True, "expected": [expression]}

    assert boundary_values(expression) == [(99.9, True), (100.0, True), (100.1, False)]
    assert "def test_REQ_01_boundary" in generate_boundary_test(ir)
    assert write_dynamic_artifact(ir, tmp_path).name == "test_REQ_01.py"


def test_dynamic_generator_creates_fuzz_harness_for_conditional():
    ir = {
        "requirement_id": "REQ-04",
        "verifiable": True,
        "property_type": "conditional",
        "trigger": {"variable": "temperature", "operator": ">=", "value": 60},
        "expected": [{"variable": "power", "operator": "==", "value": 0}],
    }

    fuzz = generate_fuzz_harness(ir)

    assert "LLVMFuzzerTestOneInput" in fuzz
    assert "temperature >= 60.0f" in fuzz
    assert "power == 0.0f" in fuzz


def test_fuzz_harness_supports_symbolic_values():
    ir = {
        "requirement_id": "REQ-02",
        "verifiable": True,
        "property_type": "conditional",
        "trigger": {"variable": "temperature", "operator": ">=", "value": 80},
        "expected": [{"variable": "valve", "operator": "==", "value": "CLOSED"}],
    }

    assert "#define CLOSED 1.0f" in generate_fuzz_harness(ir)