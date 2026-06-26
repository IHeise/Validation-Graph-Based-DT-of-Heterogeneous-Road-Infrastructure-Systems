import json


def validate_query_plan(query_plan):
    seen_ids = set()

    for step in query_plan["steps"]:
        step_id = step["id"]

        # Check uniqueness
        if step_id in seen_ids:
            return False

        dependency = step.get("dependency")

        # No dependency
        if dependency is None:
            pass

        # Regular dependency
        elif isinstance(dependency, str):
            if dependency not in seen_ids:
                return False

        # Merge dependency
        elif isinstance(dependency, dict):

            # Validate data dependencies
            for dep_id in dependency["data"]:
                if dep_id not in seen_ids:
                    return False

            # Validate mapping dependency
            if dependency["mapping"] not in seen_ids:
                return False

        else:
            return False

        seen_ids.add(step_id)

    return True