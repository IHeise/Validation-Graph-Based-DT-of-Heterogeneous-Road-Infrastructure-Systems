import importlib

def resolve_dependencies(dependency, results):
    # no dependency
    if dependency is None:
        return {}

    # single dependency
    if isinstance(dependency, str):
        return results[dependency]

    # merging dependency
    input_obj = {
        "data": [],
        "mapping": None
    }

    for dep_id in dependency["data"]:
        input_obj["data"].append(results[dep_id])

    input_obj["mapping"] = results[dependency["mapping"]]

    return input_obj




def load_function_from_path(path):
    module_path, func_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def invoke_function(function_name, dependency, results, function_map,databasename):
    if function_name not in function_map:
        raise KeyError(f"Function '{function_name}' not found in function_map")

    func = load_function_from_path(function_map[function_name])

    if dependency is None:
        return func(databasename=databasename)

    input_data = resolve_dependencies(dependency, results)

    return func(input_data,databasename=databasename)

def execute_query_plan(query_plan, function_map,databasename):
    results = {}

    for step in query_plan["steps"]:
        step_id = step["id"]

        results[step_id] = invoke_function(
            step["function"],
            step.get("dependency"),
            results,
            function_map,
            databasename
        )

    return results[query_plan["steps"][-1]["id"]]
