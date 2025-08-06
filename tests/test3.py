desired_keys = {
    "Created by": ["Created by"],
    "Written by": ["Written by"],
    "Executive producers": ["Executive producers", "Executive producer"],
    "Producers": ["Producers", "Producer"],
    "Cinematography": ["Cinematography"],
    "Editors": ["Editors", "Editor"],
}

# Flatten all variants into a single set for fast matching
all_variants = set(k for variants in desired_keys.values() for k in variants)

print(all_variants)