# a file that contains metadata to check against for the image scanner

# valid disk drive set names
valid_set_names = [
    "Swing Jazz",
    "Chaotic Metal",
    "Hormone Punk",
    "Fanged Metal",
    "Shockstar Disco",
    "Thunder Metal",
    "Woodpecker Electro",
    "Soul Rock",
    "Puffer Electro",
    "Inferno Metal",
    "Freedom Blues",
    "Polar Metal",
]

# Disk Partition 1 Main Stats
valid_partition_1_main_stats = [
    "HP",
]

# Disk Partition 2 Main Stats
valid_partition_2_main_stats = [
    "ATK",
]

# Disk Partition 3 Main Stats
valid_partition_3_main_stats = [
    "DEF",
]

# Disk Partition 4 Main Stats
valid_partition_4_main_stats = [
    "ATK",  # a percentage
    "HP",  # a percentage
    "DEF",  # a percentage
    "CRIT Rate",
    "CRIT DMG",
    "Anomaly Proficiency",
]

# Disk Partition 5 Main Stats
valid_partition_5_main_stats = [
    "HP",  # a percentage
    "DEF",  # a percentage
    "ATK",  # a percentage
    "PEN Ratio",
    "Physical DMG Bonus",
    "Fire DMG Bonus",
    "Ice DMG Bonus",
    "Electric DMG Bonus",
    "Ether DMG Bonus",
]

# Disk Partition 6 Main Stats
valid_partition_6_main_stats = [
    "HP",  # a percentage
    "DEF",  # a percentage
    "ATK",  # a percentage
    "Anomaly Mastery",
    "Impact",
    "Energy Regen",
]

# Disk Drive Ranom Stats
valid_random_stats = [
    "HP",  # flat or percentage
    "ATK",  # flat or percentage
    "DEF",  # flat or percentage
    "CRIT Rate",
    "CRIT DMG",
    "Anomaly Proficiency",
    "PEN",  # just flat
]

# Disk Drive Base Main and Sub Stat values (they are the same for each rarity)
# Sub stats increase by their base value when rolled as a rank up (eg: +1, +2, +3, etc)
# Main stats also have a base stat, and increase to 4x that value evenly until they are max level (but there is some rounding in there)
# Not entirely sure how this is split per level, but it seems to be 1/3 of the base value per level with some rounding

# TODO: Find a way to calculate the progression of the main stats with more accuracy
# NOTE: Stats not found are labeled as None
# NOTE: percentages in the progression sections have a % sign in the name if they have both a flat and percentage version
# NOTE: ATK/HP/DEF percentages are the same for all partitions
valid_b_rank_main_stats_progression = [
    ("ATK", 26),
    ("HP", 183),
    ("DEF", 15),
    ("ATK%", 2.5),
    ("HP%", 2.5),
    ("DEF%", 4),
    ("CRIT Rate", 2),
    ("CRIT DMG", 4),
    ("Anomaly Proficiency", 8),
    ("PEN Ratio", 2),
    ("Physical DMG Bonus", 2.5),
    ("Fire DMG Bonus", 2.5),
    ("Ice DMG Bonus", 2.5),
    ("Electric DMG Bonus", 2.5),
    ("Ether DMG Bonus", 2.5),
    ("Anomaly Mastery", 2.5),
    ("Impact", 1.5),
    ("Energy Regen", 5),
]

valid_b_rank_sub_stats_progression = [
    ("HP", 37),  # starts at 37, upgrades by that amount when ranked up
    ("ATK", 6),
    ("DEF", 5),
    ("HP%", 1),
    ("ATK%", 1),
    ("DEF%", 1.6),
    ("CRIT Rate", 0.8),
    ("CRIT DMG", 1.6),
    ("Anomaly Proficiency", 3),
    ("PEN", 3),
]

# A Rank Disk Drive Main and Sub Stat Progression
valid_a_rank_main_stats_progression = [
    ("ATK", 367),
    ("HP", 53),
    ("DEF", 31),
    ("ATK%", 5),
    ("HP%", 5),
    ("DEF%", 8),
    ("CRIT Rate", 4),
    ("CRIT DMG", 8),
    ("Anomaly Proficiency", 15),
    ("PEN Ratio", 4),
    ("Physical DMG Bonus", 5),
    ("Fire DMG Bonus", 5),
    ("Ice DMG Bonus", 5),
    ("Electric DMG Bonus", 5),
    ("Ether DMG Bonus", 5),
    ("Anomaly Mastery", 5),
    ("Impact", 3),
    ("Energy Regen", 10),
]

valid_a_rank_sub_stats_progression = [
    ("HP", 75),
    ("ATK", 13),
    ("DEF", 10),
    ("HP%", 2),
    ("ATK%", 2),
    ("DEF%", 3.2),
    ("CRIT Rate", 1.6),
    ("CRIT DMG", 3.2),
    ("Anomaly Proficiency", 6),
    ("PEN", 6),
]

# S Rank Disk Drive Main and Sub Stat Progression
valid_s_rank_main_stats_progression = [
    ("ATK", 79),
    ("HP", 550),
    ("DEF", 46),
    ("ATK%", 7.5),
    ("HP%", 7.5),
    ("DEF%", 12),
    ("CRIT Rate", 6),  # externally sourced
    ("CRIT DMG", 12),  # externally sourced
    ("Anomaly Proficiency", 23),  # externally sourced
    ("PEN Ratio", 6),
    ("Physical DMG Bonus", 7.5),
    ("Fire DMG Bonus", 7.5),
    ("Ice DMG Bonus", 7.5),
    ("Electric DMG Bonus", 7.5),
    ("Ether DMG Bonus", 7.5),
    ("Anomaly Mastery", 7.5),
    ("Impact", 4.5),  # externally sourced
    ("Energy Regen", 15),
]

valid_s_rank_sub_stats_progression = [
    ("HP", 112),
    ("ATK", 19),
    ("DEF", 15),
    ("HP%", 3),
    ("ATK%", 3),
    ("DEF%", 4.8),
    ("CRIT Rate", 2.4),
    ("CRIT DMG", 4.8),
    ("Anomaly Proficiency", 9),
    ("PEN", 9),
]


def get_rarity_stats(rarity):
    if rarity == "B":
        return valid_b_rank_main_stats_progression, valid_b_rank_sub_stats_progression
    elif rarity == "A":
        return valid_a_rank_main_stats_progression, valid_a_rank_sub_stats_progression
    elif rarity == "S":
        return valid_s_rank_main_stats_progression, valid_s_rank_sub_stats_progression
    else:
        return None


def get_partition_main_stats(partition):
    if partition == 1:
        return valid_partition_1_main_stats
    elif partition == 2:
        return valid_partition_2_main_stats
    elif partition == 3:
        return valid_partition_3_main_stats
    elif partition == 4:
        return valid_partition_4_main_stats
    elif partition == 5:
        return valid_partition_5_main_stats
    elif partition == 6:
        return valid_partition_6_main_stats
    else:
        return None


def get_rarity_from_maxLevel(maxLevel):
    if maxLevel == 15:
        return "S"
    elif maxLevel == 12:
        return "A"
    elif maxLevel == 9:
        return "B"
    else:
        return None


# a function to validate the main stat value of a disk drive within validate_disk_drive
def validate_main_stat_value(
    main_stat_name, main_stat_value, main_stats_progression, curLevel, maxLevel
):
    # we know the main stat name is valid, we need to check if its value is valid

    # find the base value for this main stat from the progression
    base_value = None
    for stat_name, value in main_stats_progression:
        if stat_name == main_stat_name:
            base_value = value
            break
    if base_value == None:  # check if the main stat name is valid
        return False

    # calculate the range for this stat (base -> 4 * base)
    min_value = base_value
    max_value = base_value * 4

    # check if the value is within the range
    if main_stat_value < min_value or main_stat_value > max_value:
        return False

    # calculate what the value should be at the current level
    # the stat progression is split evenly across the levels
    progression_per_level = (max_value - min_value) / (
        maxLevel
    )  # remainder is kept until greater than 1, then added to the value next level
    # as such, the expected value will be rounded down to the nearest whole number
    # floor division will round down
    expected_value = (min_value + (progression_per_level * curLevel)) // 1

    # check if the value is correct
    if (
        main_stat_value != expected_value
    ):  # NOTE: might add some looseness to this check later
        return False

    return True


# a function to validate the sub stat value of a disk drive within validate_disk_drive
# sub_stats is a list of tuples of the sub stat name and value
def validate_sub_stat_value(sub_stats, sub_stats_progression, curLevel, maxLevel):
    # first, make sure all sub stats are valid
    for sub_stat_name, sub_stat_value in sub_stats:
        if sub_stat_name not in valid_random_stats:
            return False

    # calculate the number of expected rank-ups (one per 3 levels)
    expected_rank_ups = curLevel // 3

    # get the sub stats that are ranked up (eg: have a +X value after the name)
    ranked_up_sub_stats = []
    for sub_stat_name, sub_stat_value in sub_stats:
        if "+" in sub_stat_name:
            ranked_up_sub_stats.append((sub_stat_name, sub_stat_value))
        else:
            # check if the value is correct - it should be the base value
            base_value = None
            for stat_name, value in sub_stats_progression:
                if (
                    stat_name == sub_stat_name
                ):  # we know there will be matching names as we checked for valid sub stats earlier
                    base_value = value
                    if sub_stat_value != base_value:
                        return False

    # calculate the total number of rank ups across all ranked up sub stats (eg: if one is +3 and another is +2, the total is 5)
    total_rank_ups = 0
    for sub_stat_name, sub_stat_value in ranked_up_sub_stats:
        rank_up_number = int(sub_stat_name.split("+")[1])
        total_rank_ups += rank_up_number
        # for each ranked up sub stat, check if the value is correct
        # it should be the base value + (rank_up_number * base value)
        base_value = None
        for stat_name, value in sub_stats_progression:
            if stat_name == sub_stat_name:
                base_value = value
                break
        expected_rank_up_value = base_value + (rank_up_number * base_value)
        if sub_stat_value != expected_rank_up_value:
            return False

    # check if the total rank ups is correct
    if total_rank_ups != expected_rank_ups:
        return False

    return True


# A function to validate the metadata of a disk drive
# main stat is a tuple of the main stat name and value
# sub stats is a list of tuples of the sub stat name and value
def validate_disk_drive(set_name, curLevel, maxLevel, partition, main_stat, sub_stats):
    # check if the set name is valid
    if set_name not in valid_set_names:
        return False
    rarity = get_rarity_from_maxLevel(maxLevel)
    if rarity == None:  # check if the max level is valid
        return False
    # check if current level is valid
    if curLevel < 0 or curLevel > maxLevel:
        return False

    valid_main_stats = get_partition_main_stats(partition)
    (main_stat_name, main_stat_value) = main_stat
    if valid_main_stats == None:  # check if the partition is valid
        return False
    if main_stat_name not in valid_main_stats:
        return False  # check if the main stat is valid for the partition

    # check if the main stat value is valid
    main_stats_progression, sub_stats_progression = get_rarity_stats(rarity)
    if not validate_main_stat_value(
        main_stat_name, main_stat_value, main_stats_progression, curLevel, maxLevel
    ):
        return False

    # check if the sub stat values are valid
    if not validate_sub_stat_value(
        sub_stats, sub_stats_progression, curLevel, maxLevel
    ):
        return False

    return True
