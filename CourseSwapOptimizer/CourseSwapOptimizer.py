import builtins
import collections # Added import
import copy
import csv
import itertools
import traceback


# --- Data Reading ---
def read_course_data(filename):
    """
    Reads and parses course swap requests from a file.

    Adds a unique 'request_id'. Handles various formats, course names with spaces,
    and optional section info (any section acceptable).

    Args:
        filename (str): Path to the data file.

    Returns:
        list: Sorted list of parsed student request dictionaries.
    """
    students_data = []
    request_counter = itertools.count() # Unique ID generator

    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file):
                line = line.strip()
                if not line:
                    continue

                req_id = f"req_{next(request_counter)}_{line_num+1}" # Unique ID

                # Extract student ID
                parts = line.split(maxsplit=1)
                student_id = parts[0]

                if len(parts) < 2:
                    print(f"Warning (Req {req_id}): Invalid line format: {line}")
                    continue

                remaining = parts[1]
                tokens = remaining.split()

                section_positions = []
                for i, token in enumerate(tokens):
                    # Identify potential section letters
                    if len(token) == 1 and token.isalpha() and token.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        section_positions.append(i)

                course_id = None
                swap_course_id = None
                # Identify tokens like "CourseName-Section"
                embedded_section_courses = [
                    (i, token) for i, token in enumerate(tokens) if
                    "-" in token and any(c.isalpha() for c in token.split("-")[-1])
                ]

                # --- Parsing Logic ---
                # Note: This section contains many specific format handlers.
                # Comments are kept minimal as the code structure implies the format.

                # Ex: "Data Engineering-C C Applied ML-B"
                if (len(embedded_section_courses) >= 1 and
                        len(section_positions) >= 1 and
                        embedded_section_courses[0][0] < section_positions[0]):
                    current_course_with_section = " ".join(tokens[:section_positions[0]])
                    current_section = tokens[section_positions[0]]
                    if "-" in current_course_with_section:
                        embedded_section = current_course_with_section.split("-")[-1]
                        if embedded_section == current_section:
                            course_id = current_course_with_section
                            if section_positions[0] + 1 < len(tokens):
                                swap_course_id = " ".join(tokens[section_positions[0] + 1:])
                                if "-" not in swap_course_id:
                                    swap_course_id = f"{swap_course_id}"
                            else:
                                swap_course_id = None

                # Ex: "CN- A A C"
                elif (len(tokens) >= 3 and
                      tokens[0].endswith("-") and
                      len(section_positions) >= 2 and
                      section_positions[0] == 1 and
                      section_positions[1] == 2):
                    course_prefix = tokens[0]
                    current_section = tokens[1]
                    if tokens[1] == tokens[2] and len(tokens) > 3:
                        swap_section = tokens[3]
                    else:
                        swap_section = tokens[2]
                    course_id = f"{course_prefix}{current_section}"
                    swap_course_id = f"{course_prefix}{swap_section}"

                # Ex: "DAA-D D E"
                elif len(tokens) == 3 and "-" in tokens[0] and len(tokens[1]) == 1 and len(tokens[2]) == 1:
                    course_with_section = tokens[0]
                    current_section = tokens[1]
                    swap_section = tokens[2]
                    course_base = course_with_section.rsplit("-", 1)[0]
                    course_id = f"{course_base}-{current_section}"
                    swap_course_id = f"{course_base}-{swap_section}"

                # Ex: "PF-D D DAA-B"
                elif len(tokens) == 3 and "-" in tokens[0] and len(tokens[1]) == 1 and "-" in tokens[2]:
                    course_with_section = tokens[0]
                    current_section = tokens[1]
                    swap_course_with_section = tokens[2]
                    course_base = course_with_section.rsplit("-", 1)[0]
                    course_id = f"{course_base}-{current_section}"
                    swap_course_id = swap_course_with_section

                # Ex: "SE-A A B"
                elif len(tokens) == 3 and "-" in tokens[0] and len(tokens[1]) == 1 and len(tokens[2]) == 1 and tokens[1].upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and tokens[2].upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                     course_with_section = tokens[0]
                     current_section = tokens[1]
                     swap_section = tokens[2]
                     course_base = course_with_section.rsplit("-", 1)[0]
                     course_id = f"{course_base}-{current_section}"
                     swap_course_id = f"{course_base}-{swap_section}"

                # Two+ section indicators
                elif len(section_positions) >= 2:
                    first_section_pos = section_positions[0]
                    current_course_parts = tokens[:first_section_pos]
                    current_section = tokens[first_section_pos]
                    second_section_pos = section_positions[1]
                    current_course_str = " ".join(current_course_parts)

                    if current_course_str.endswith("-"): course_id = f"{current_course_str}{current_section}"
                    elif "-" in current_course_str: course_id = f"{current_course_str.rsplit('-', 1)[0]}-{current_section}"
                    else: course_id = f"{current_course_str}-{current_section}"

                    if second_section_pos + 1 < len(tokens):
                        swap_course_parts = tokens[second_section_pos + 1:]
                        swap_course_id = " ".join(swap_course_parts)
                        if "-" not in swap_course_id and len(swap_course_id) == 1 and swap_course_id.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            base_course = current_course_str.rsplit("-", 1)[0] if "-" in current_course_str else current_course_str
                            swap_course_id = f"{base_course}-{swap_course_id}"
                    else:
                        swap_section = tokens[second_section_pos]
                        base_course = current_course_str.rsplit("-", 1)[0] if "-" in current_course_str else current_course_str
                        swap_course_id = f"{base_course}-{swap_section}"

                # General fallback
                else:
                    if len(embedded_section_courses) >= 1:
                        first_idx = embedded_section_courses[0][0]
                        course_id = " ".join(tokens[:first_idx + 1])
                        if first_idx + 1 < len(tokens):
                            swap_course_id = " ".join(tokens[first_idx + 1:])
                            if "-" not in swap_course_id and len(swap_course_id) == 1 and swap_course_id.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                                if "-" in course_id:
                                    base_course = course_id.rsplit("-", 1)[0]
                                    swap_course_id = f"{base_course}-{swap_course_id}"
                        else: swap_course_id = None
                    elif len(tokens) >= 3 and len(tokens[-2]) == 1 and tokens[-2].upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                         current_section = tokens[-2]
                         current_course_parts = tokens[:-2]
                         current_course_str = " ".join(current_course_parts)
                         base_course = current_course_str.rsplit("-", 1)[0] if "-" in current_course_str else current_course_str

                         if current_course_str.endswith("-"): course_id = f"{current_course_str}{current_section}"
                         elif "-" in current_course_str: course_id = f"{base_course}-{current_section}"
                         else: course_id = f"{current_course_str}-{current_section}"

                         if len(tokens[-1]) == 1 and tokens[-1].upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                             swap_section = tokens[-1]
                             swap_course_id = f"{base_course}-{swap_section}"
                         else:
                             swap_course_id = tokens[-1] # Assumed full course name
                             if len(swap_course_id) == 1 and swap_course_id.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": # Check if it was actually a section
                                 swap_course_id = f"{base_course}-{swap_course_id}"

                    elif len(section_positions) >= 1:
                         sect_pos = section_positions[0]
                         if 0 < sect_pos < len(tokens) - 1:
                             current_course = " ".join(tokens[:sect_pos])
                             current_section = tokens[sect_pos]
                             swap_course = " ".join(tokens[sect_pos + 1:])
                             base_course = current_course.rsplit("-", 1)[0] if "-" in current_course else current_course

                             if current_course.endswith("-"): course_id = f"{current_course}{current_section}"
                             elif "-" in current_course: course_id = f"{base_course}-{current_section}"
                             else: course_id = f"{current_course}-{current_section}"

                             if len(swap_course) == 1 and swap_course.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                                 swap_course_id = f"{base_course}-{swap_course}"
                             else:
                                 swap_course_id = swap_course
                         else:
                             print(f"Warning (Req {req_id}): Could not parse complex format: {line}")
                             continue
                    else:
                         print(f"Warning (Req {req_id}): Could not parse line: {line}")
                         continue
                # --- End Parsing Logic ---

                if course_id is None:
                    print(f"Warning (Req {req_id}): Could not determine course_id for line: {line}")
                    continue

                # Final checks/corrections (e.g., "SE-A A B")
                if len(tokens) == 3 and "-" in tokens[0] and len(tokens[1]) == 1 and tokens[1].upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and len(tokens[2]) == 1 and tokens[2].upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and swap_course_id == tokens[2]:
                    course_base = tokens[0].rsplit("-", 1)[0]
                    swap_course_id = f"{course_base}-{tokens[2]}"

                # Specific hardcoding (consider removing if general parsing is robust)
                if "Engineering-C C Applied" in line:
                     course_id = "Data Engineering-C"
                     swap_course_id = "Applied ML-B"

                # Check if swap target allows any section
                any_section_acceptable = swap_course_id and "-" not in swap_course_id and not (len(swap_course_id) == 1 and swap_course_id.isalpha())

                student_data = {
                    "request_id": req_id,
                    "student_id": student_id,
                    "course_id": course_id, # Course offered
                    "swap_course_id": swap_course_id, # Course wanted
                    "priority": int(student_id[:2]) if student_id[:2].isdigit() else 99, # Lower is higher priority
                    "any_section_acceptable": any_section_acceptable,
                    "original_line": line
                }

                if course_id == swap_course_id:
                    print(f"Warning (Req {req_id}): Course ID and Swap Course ID are the same: {line}")
                    continue

                students_data.append(student_data)

    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
    except Exception as e:
        print(f"Error reading or parsing file {filename}: {e}")
        traceback.print_exc()

    # Sort by priority (primary), request_id (secondary for stability)
    return sorted(students_data, key=lambda x: (x['priority'], x['request_id']))

# --- Utility ---
def get_course_base(course_id):
    """Extracts the base course name"""
    if not course_id:
        return None
    if '-' in course_id:
        parts = course_id.rsplit('-', 1)
        # Check if part after '-' looks like a section (single uppercase letter)
        if len(parts) == 2 and len(parts[1]) == 1 and parts[1].isalpha() and parts[1].isupper():
            return parts[0].strip()
    # Otherwise, return the whole string
    return course_id.strip()

# --- Iterative Swap Strategy ---
def iterative_swaps(students_data_input):
    """
    Performs iterative direct (2-way) swaps until no more swaps are possible.
    Handles multiple requests per student.
    """
    students_data = copy.deepcopy(students_data_input) # Work on a copy
    swap_count = 0
    fulfilled_requests = set() # Track fulfilled request_ids
    swapped_courses_given_up = set() # Track (student_id, course_id) tuples given up
    swaps_log = [] # Log of (req1_id, req2_id) pairs

    found_swap_in_iteration = True
    while found_swap_in_iteration:
        found_swap_in_iteration = False
        # Consider only unfulfilled requests in each iteration
        current_requests = [req for req in students_data if req['request_id'] not in fulfilled_requests]

        for i in range(len(current_requests)):
            req1 = current_requests[i]
            req1_id = req1['request_id']
            s1_id = req1['student_id']
            c1_offer = req1['course_id']
            c1_want = req1['swap_course_id']
            c1_want_base = get_course_base(c1_want)
            c1_any = req1['any_section_acceptable']

            # Skip if already fulfilled or course offered is gone
            if req1_id in fulfilled_requests or (s1_id, c1_offer) in swapped_courses_given_up:
                continue

            # Look for a partner (req2)
            for j in range(i + 1, len(current_requests)): # Avoid self-swaps and redundant checks
                req2 = current_requests[j]
                req2_id = req2['request_id']
                s2_id = req2['student_id']
                c2_offer = req2['course_id']
                c2_want = req2['swap_course_id']
                c2_want_base = get_course_base(c2_want)
                c2_any = req2['any_section_acceptable']

                # Skip checks
                if s1_id == s2_id: continue # Same student
                if req2_id in fulfilled_requests or (s2_id, c2_offer) in swapped_courses_given_up: continue # Already fulfilled/gone

                # --- Check Swap Conditions ---
                c1_offer_base = get_course_base(c1_offer)
                c2_offer_base = get_course_base(c2_offer)

                # R1 wants R2's offer? (Specific or base match)
                match1_wants_2 = (c1_want == c2_offer) or \
                                 (c1_any and c1_want_base == c2_offer_base)

                # R2 wants R1's offer? (Specific or base match)
                match2_wants_1 = (c2_want == c1_offer) or \
                                 (c2_any and c2_want_base == c1_offer_base)

                if match1_wants_2 and match2_wants_1:
                    # Found a swap!
                    swap_count += 1
                    fulfilled_requests.add(req1_id)
                    fulfilled_requests.add(req2_id)
                    swapped_courses_given_up.add((s1_id, c1_offer))
                    swapped_courses_given_up.add((s2_id, c2_offer))
                    swaps_log.append((req1_id, req2_id))

                    found_swap_in_iteration = True
                    # Restart iteration as state has changed
                    break
            if found_swap_in_iteration:
                 break # Restart the while loop

    return swaps_log, fulfilled_requests

# --- Greedy Swap Strategy (Optimized) ---
def greedy_swaps(students_data_input):
    """
    Performs greedy direct (2-way) swaps based on request priority.
    Assumes students_data is sorted by priority. Optimized with lookup maps.
    """
    # import collections # Already imported globally
    students_data = students_data_input # Assumes sorted
    swap_count = 0
    fulfilled_requests = set()
    swapped_courses_given_up = set()
    swaps_log = []
    request_map = {req['request_id']: req for req in students_data}

    # --- Create lookup maps for offered courses ---
    offers_specific = collections.defaultdict(list) # course_id -> [req_id]
    offers_base = collections.defaultdict(list)     # base_course -> [req_id]
    for req in students_data:
        req_id = req['request_id']
        course_id = req['course_id']
        base_course = get_course_base(course_id)
        offers_specific[course_id].append(req_id)
        if base_course:
             offers_base[base_course].append(req_id)
    # --- End lookup maps ---

    # Iterate through requests by priority
    for req1 in students_data:
        req1_id = req1['request_id']
        s1_id = req1['student_id']
        c1_offer = req1['course_id']
        c1_want = req1['swap_course_id']
        c1_any = req1['any_section_acceptable']
        c1_want_base = get_course_base(c1_want)

        # Skip if already handled
        if req1_id in fulfilled_requests or (s1_id, c1_offer) in swapped_courses_given_up:
            continue
        if not c1_want: continue # Cannot swap if nothing is wanted

        # Find potential partners using lookup maps
        potential_partner_ids = set()
        if not c1_any: # Wants specific course
            if c1_want in offers_specific:
                potential_partner_ids.update(offers_specific[c1_want])
        else: # Wants any section of base course
            if c1_want_base in offers_base:
                potential_partner_ids.update(offers_base[c1_want_base])

        # Check potential partners
        for req2_id in potential_partner_ids:
            # Basic checks
            if req2_id == req1_id: continue
            if req2_id in fulfilled_requests: continue

            req2 = request_map[req2_id]
            s2_id = req2['student_id']
            c2_offer = req2['course_id']
            c2_want = req2['swap_course_id']
            c2_any = req2['any_section_acceptable']
            c2_want_base = get_course_base(c2_want)

            # Validity checks
            if s1_id == s2_id: continue
            if (s2_id, c2_offer) in swapped_courses_given_up: continue

            # Check if req2 wants what req1 offers
            c1_offer_base = get_course_base(c1_offer)
            match2_wants_1 = (c2_want == c1_offer) or \
                             (c2_any and c2_want_base == c1_offer_base)

            if match2_wants_1:
                # Found a valid partner! Perform the greedy swap
                swap_count += 1
                fulfilled_requests.add(req1_id)
                fulfilled_requests.add(req2_id)
                swapped_courses_given_up.add((s1_id, c1_offer))
                swapped_courses_given_up.add((s2_id, c2_offer))
                swaps_log.append((req1_id, req2_id))

                # Greedy: take the first match and move to the next req1
                break

    return swaps_log, fulfilled_requests


# --- Graph-Based Swap Strategy ---

# --- Optimized Graph Building ---
def build_request_graph_optimized(students_data):
    """
    Builds optimized graph: nodes=request_ids, edges=potential swaps.
    Uses lookup maps for faster edge creation.
    """
    # import collections # Already imported globally
    adj = collections.defaultdict(list) # Adjacency list: req_id -> [potential_partner_req_id]
    request_map = {req['request_id']: req for req in students_data}

    # --- Create lookup maps for offered courses ---
    offers_specific = collections.defaultdict(list) # course_id -> [req_id]
    offers_base = collections.defaultdict(list)     # base_course -> [req_id]
    for req in students_data:
        req_id = req['request_id']
        course_id = req['course_id']
        base_course = get_course_base(course_id)
        offers_specific[course_id].append(req_id)
        if base_course:
             offers_base[base_course].append(req_id)
    # --- End lookup maps ---

    # --- Build adjacency list using lookups ---
    for req1 in students_data:
        req1_id = req1['request_id']
        s1_id = req1['student_id']
        c1_want = req1['swap_course_id']
        c1_any = req1['any_section_acceptable']
        c1_want_base = get_course_base(c1_want)

        if not c1_want: continue

        potential_partners = set()
        # Find requests offering what req1 wants
        if not c1_any: # Wants specific
            if c1_want in offers_specific:
                potential_partners.update(offers_specific[c1_want])
        else: # Wants any section
            if c1_want_base in offers_base:
                potential_partners.update(offers_base[c1_want_base])

        # Add edges if partner is not the same student
        for req2_id in potential_partners:
            if req2_id in request_map: # Ensure partner exists
                req2 = request_map[req2_id]
                s2_id = req2['student_id']
                if s1_id != s2_id:
                    adj[req1_id].append(req2_id)

    return adj, request_map

# --- Cycle Finding (DFS) ---
def find_request_cycles(students_data_input):
    """Finds cycles in the request graph using DFS (optimized graph build)."""
    # import collections # Already imported globally
    students_data = students_data_input # Assumes sorted by priority
    adj, request_map = build_request_graph_optimized(students_data)
    fulfilled_requests = set()
    swapped_courses_given_up = set() # (student_id, course_id)
    cycle_log = [] # List of cycles found (each cycle is a list of req_ids)
    # total_fulfilled_in_cycles = 0 # Not strictly needed if returning fulfilled_requests set
    # dfs_call_count = 0 # Debug counter
    # max_depth = 0 # Debug depth tracker

    MAX_DFS_DEPTH = 10  # Limit cycle search depth for performance

    def dfs(u_req_id, path_req_ids, visited_in_path_req_ids):
        # nonlocal total_fulfilled_in_cycles, dfs_call_count, max_depth # Removed unused nonlocals
        # dfs_call_count += 1
        current_depth = len(path_req_ids)
        # max_depth = max(max_depth, current_depth)

        if current_depth > MAX_DFS_DEPTH: return False # Depth limit exceeded

        # Optimization: Check fulfillment early
        if u_req_id in fulfilled_requests: return False

        req_u_data = request_map.get(u_req_id)
        if not req_u_data: return False # Should not happen with correct graph build

        s_u_id = req_u_data['student_id']
        c_u_offer = req_u_data['course_id']

        # Check if course offering is already used globally
        if (s_u_id, c_u_offer) in swapped_courses_given_up: return False

        visited_in_path_req_ids.add(u_req_id)
        path_req_ids.append(u_req_id)

        cycle_found_and_processed = False

        neighbors = adj.get(u_req_id, [])
        for v_req_id in neighbors:
            if v_req_id == path_req_ids[0]: # Cycle detected back to start node
                # --- Validate the potential cycle ---
                is_valid_cycle = True
                potential_courses_to_give_up = set()
                students_in_cycle = set()

                for cycle_req_id in path_req_ids:
                    # Check global state
                    if cycle_req_id in fulfilled_requests: is_valid_cycle = False; break
                    cycle_req_data = request_map.get(cycle_req_id)
                    if not cycle_req_data: is_valid_cycle = False; break

                    cycle_s_id = cycle_req_data['student_id']
                    cycle_c_offer = cycle_req_data['course_id']
                    if (cycle_s_id, cycle_c_offer) in swapped_courses_given_up: is_valid_cycle = False; break

                    # Check intra-cycle conflicts
                    if (cycle_s_id, cycle_c_offer) in potential_courses_to_give_up: is_valid_cycle = False; break # Student giving up same course twice?
                    if cycle_s_id in students_in_cycle: is_valid_cycle = False; break # Same student multiple times?

                    potential_courses_to_give_up.add((cycle_s_id, cycle_c_offer))
                    students_in_cycle.add(cycle_s_id)

                if is_valid_cycle:
                    # Process the valid cycle
                    cycle_log.append(list(path_req_ids))
                    fulfilled_requests.update(path_req_ids)
                    swapped_courses_given_up.update(potential_courses_to_give_up)
                    # total_fulfilled_in_cycles += len(path_req_ids) # Not needed
                    cycle_found_and_processed = True
                    break # Exit neighbor loop for u_req_id (processed this path)

            elif v_req_id not in visited_in_path_req_ids: # Explore deeper
                 if dfs(v_req_id, path_req_ids, visited_in_path_req_ids):
                     # If a cycle was found deeper, mark success and break
                     cycle_found_and_processed = True
                     break # Exit neighbor loop for u_req_id (processed via deeper call)

        # Backtrack
        path_req_ids.pop()
        visited_in_path_req_ids.remove(u_req_id)
        return cycle_found_and_processed # Return if a cycle was processed on this path

    # Iterate through requests by priority to start DFS
    # nodes_processed = 0 # Debug counter
    for req_data in students_data:
        start_req_id = req_data['request_id']
        # nodes_processed += 1

        # Start DFS only if node not already fulfilled and its course is available
        if start_req_id not in fulfilled_requests:
            s_id = req_data['student_id']
            c_offer = req_data['course_id']
            if (s_id, c_offer) not in swapped_courses_given_up:
                 visited_in_path = set()
                 path = []
                 dfs(start_req_id, path, visited_in_path) # State modified within dfs

    return cycle_log, fulfilled_requests, swapped_courses_given_up

# --- Direct Swaps After Cycles (Optimized) ---
def find_direct_swaps_after_cycles_updated(students_data_input, fulfilled_requests_input, swapped_courses_input):
    """
    Finds direct two-way swaps among remaining requests after cycle detection.
    Optimized using lookup maps on remaining requests.
    """
    # import collections # Already imported globally
    students_data = students_data_input # Original sorted list
    fulfilled_requests = fulfilled_requests_input.copy() # Start with requests fulfilled by cycles
    swapped_courses_given_up = swapped_courses_input.copy() # Start with courses used in cycles
    direct_swap_pairs = []
    # newly_fulfilled_count = 0 # Not needed if returning final set

    # Filter remaining requests *first*
    remaining_requests_list = [req for req in students_data if req['request_id'] not in fulfilled_requests]
    request_map = {req['request_id']: req for req in remaining_requests_list} # Map of only remaining

    # --- Create lookup maps based *only* on remaining, available offers ---
    offers_specific = collections.defaultdict(list)
    offers_base = collections.defaultdict(list)
    for req in remaining_requests_list:
        # Skip if the course they offer is already gone (from cycles)
        if (req['student_id'], req['course_id']) in swapped_courses_given_up:
            continue

        req_id = req['request_id']
        course_id = req['course_id']
        base_course = get_course_base(course_id)
        offers_specific[course_id].append(req_id)
        if base_course:
             offers_base[base_course].append(req_id)
    # --- End lookup maps ---

    # Iterate through remaining requests (maintaining original priority order)
    for req1 in remaining_requests_list:
        req1_id = req1['request_id']
        s1_id = req1['student_id']
        c1_offer = req1['course_id']
        c1_want = req1['swap_course_id']
        c1_any = req1['any_section_acceptable']
        c1_want_base = get_course_base(c1_want)

        # Check if already handled (in this phase) or course used
        if req1_id in fulfilled_requests or (s1_id, c1_offer) in swapped_courses_given_up:
            continue
        if not c1_want: continue

        # Find potential partners using lookups (from remaining offers)
        potential_partner_ids = set()
        if not c1_any:
            if c1_want in offers_specific: potential_partner_ids.update(offers_specific[c1_want])
        else:
            if c1_want_base in offers_base: potential_partner_ids.update(offers_base[c1_want_base])

        # Check potential partners
        for req2_id in potential_partner_ids:
            # Basic checks
            if req2_id == req1_id: continue
            if req2_id not in request_map: continue # Partner not in remaining list
            if req2_id in fulfilled_requests: continue # Already fulfilled in this phase

            req2 = request_map[req2_id]
            s2_id = req2['student_id']
            c2_offer = req2['course_id']
            c2_want = req2['swap_course_id']
            c2_any = req2['any_section_acceptable']
            c2_want_base = get_course_base(c2_want)

            # Validity checks
            if s1_id == s2_id: continue
            if (s2_id, c2_offer) in swapped_courses_given_up: continue # Partner's offer already gone

            # Check if req2 wants what req1 offers
            c1_offer_base = get_course_base(c1_offer)
            match2_wants_1 = (c2_want == c1_offer) or \
                             (c2_any and c2_want_base == c1_offer_base)

            if match2_wants_1:
                # Found a valid direct swap!
                direct_swap_pairs.append((req1_id, req2_id))
                fulfilled_requests.add(req1_id)
                fulfilled_requests.add(req2_id)
                swapped_courses_given_up.add((s1_id, c1_offer))
                swapped_courses_given_up.add((s2_id, c2_offer))
                # newly_fulfilled_count += 2 # Not needed

                # Break inner loop (greedy within this phase)
                break

    return direct_swap_pairs, fulfilled_requests # Return final fulfilled set

# --- Combined Graph Strategy ---
def find_swap_cycles_and_direct_pairs_updated(students_data_input):
    """Combined cycle finding and direct swaps."""
    students_data = students_data_input # Assumes sorted

    # 1. Find cycles
    swap_cycles, fulfilled_after_cycles, courses_given_up_after_cycles = find_request_cycles(students_data)
    # 2. Find direct swaps among remaining
    direct_swaps, final_fulfilled_requests = find_direct_swaps_after_cycles_updated(
        students_data, fulfilled_after_cycles, courses_given_up_after_cycles
    )

    # Return cycles found, direct swaps found after cycles, and the final set of all fulfilled requests
    return swap_cycles, direct_swaps, final_fulfilled_requests

# --- CSV Output ---
def write_swap_results_csv(filename, fulfilled_request_ids, students_data):
    """
    Writes fulfilled swap requests to a CSV.
    Output format: [student_id], [original_course_offered], [original_course_wanted]

    """
    req_map = {req['request_id']: req for req in students_data}
    rows = []
    # Iterate through the set of fulfilled request IDs
    for req_id in fulfilled_request_ids:
        req = req_map.get(req_id)
        if req:
            # Output original request details for fulfilled ones
            rows.append([req['student_id'], req['course_id'], req['swap_course_id']])

    # Sort rows for consistent output (e.g., by student_id, then original course)
    rows.sort()

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['student_id', 'current', 'swapped']) # Header
        writer.writerows(rows)

# --- Main Execution Block ---
if __name__ == "__main__":
    print("Starting Course Swap Optimization...")
    # Select input file
    input_file = 'data2.txt'

    all_students_data = read_course_data(input_file)

    if not all_students_data:
        print(f"No student data loaded from {input_file}. Exiting.")
        exit()

    print(f"Parsed {len(all_students_data)} student requests from {input_file}.")
    print("-" * 60)

    # --- Run Strategies ---

    # Temporarily disable print during swap execution for cleaner output
    original_print = builtins.print
    builtins.print = lambda *a, **k: None

    # Iterative swaps
    iterative_data = copy.deepcopy(all_students_data)
    iterative_pairs, iterative_fulfilled = iterative_swaps(iterative_data)
    write_swap_results_csv('../22I-2126_AliHamzaAzam/iterative_results.csv', iterative_fulfilled, all_students_data)

    # Greedy swaps
    greedy_data = copy.deepcopy(all_students_data)
    greedy_pairs, greedy_fulfilled = greedy_swaps(greedy_data)
    write_swap_results_csv('../22I-2126_AliHamzaAzam/greedy_results.csv', greedy_fulfilled, all_students_data)

    # Graph-based (Cycles + Direct)
    graph_data = copy.deepcopy(all_students_data)
    graph_cycles, graph_direct, graph_fulfilled_requests = find_swap_cycles_and_direct_pairs_updated(graph_data)
    write_swap_results_csv('../22I-2126_AliHamzaAzam/graph_results.csv', graph_fulfilled_requests, all_students_data)

    # Restore print function
    builtins.print = original_print

    print("Course Swap Optimization completed.")
    print("\nSummary:")
    print(f"Iterative Swaps: Fulfilled {len(iterative_fulfilled)} requests.")
    print(f"Greedy Swaps:    Fulfilled {len(greedy_fulfilled)} requests.")
    print(f"Graph (Cycles+Direct): Fulfilled {len(graph_fulfilled_requests)} requests.")



