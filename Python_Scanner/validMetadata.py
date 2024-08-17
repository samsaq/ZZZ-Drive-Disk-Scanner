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
    ("ATK", 53),
    ("HP", 367),
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
    ("CRIT Rate", 6),  # externally sourced + percentage
    ("CRIT DMG", 12),  # externally sourced + percentage
    ("Anomaly Proficiency", 23),  # externally sourced
    ("PEN Ratio", 6),  # percentage
    ("Physical DMG Bonus", 7.5),  # percentage
    ("Fire DMG Bonus", 7.5),  # percentage
    ("Ice DMG Bonus", 7.5),  # percentage
    ("Electric DMG Bonus", 7.5),  # percentage
    ("Ether DMG Bonus", 7.5),  # percentage
    ("Anomaly Mastery", 7.5),  # percentage
    ("Impact", 4.5),  # externally sourced + percentage
    ("Energy Regen", 15),  # percentage
]

valid_s_rank_sub_stats_progression = [
    ("HP", 112),
    ("ATK", 19),
    ("DEF", 15),
    ("HP%", 3),  # percentage
    ("ATK%", 3),  # percentage
    ("DEF%", 4.8),  # percentage
    ("CRIT Rate", 2.4),  # percentage
    ("CRIT DMG", 4.8),  # percentage
    ("Anomaly Proficiency", 9),
    ("PEN", 9),
]

# list of main stats that are percentage based
percentage_main_stats = [
    "ATK%",
    "HP%",
    "DEF%",
    "CRIT Rate",
    "CRIT DMG",
    "Anomaly Proficiency",
    "PEN Ratio",
    "Physical DMG Bonus",
    "Fire DMG Bonus",
    "Ice DMG Bonus",
    "Electric DMG Bonus",
    "Ether DMG Bonus",
    "Anomaly Mastery",
    "Impact",
    "Energy Regen",
]

# list of sub stats that are percentage based
percentage_sub_stats = [
    "HP%",
    "ATK%",
    "DEF%",
    "CRIT Rate",
    "CRIT DMG",
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
    partition = int(partition)
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
    maxLevel = int(maxLevel)
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
    curLevel = int(curLevel)
    maxLevel = int(maxLevel)
    # remove main stat value % sign and any characters after it

    main_stat_value_str = main_stat_value
    if "%" in main_stat_value:
        main_stat_value = main_stat_value.split("%")[0]
        if any(keyword in main_stat_name for keyword in ["ATK", "HP", "DEF"]):
            main_stat_name += "%"
    main_stat_value = float(main_stat_value)

    # we know the main stat name is valid, we need to check if its value is valid

    # find the base value for this main stat from the progression
    base_value = None
    for stat_name, value in main_stats_progression:
        if stat_name == main_stat_name:
            base_value = value
            break
    if base_value == None:  # check if the main stat name is valid
        return (False, "Invalid main stat name")

    # calculate the range for this stat (base -> 4 * base)
    min_value = base_value
    max_value = base_value * 4

    # check if the value is within the range
    if main_stat_value < min_value or main_stat_value > max_value:
        return (False, "Main stat value out of expected range")

    # calculate what the value should be at the current level
    # the stat progression is split evenly across the levels
    progression_per_level = (max_value - min_value) / (
        maxLevel
    )  # remainder is kept until greater than 1, then added to the value next level
    # as such, the expected value will be rounded down to the nearest whole number
    # floor division will round down
    expected_value_int = (min_value + (progression_per_level * curLevel)) // 1

    # for percentage based stats, the expected value has no rounding
    expected_value_percentage = min_value + (progression_per_level * curLevel)

    if any(keyword in main_stat_name for keyword in percentage_main_stats):
        expected_value = expected_value_percentage
    else:
        expected_value = expected_value_int

    # check if the value is correct
    tolerance = 0.05
    if (
        abs(main_stat_value - expected_value) > tolerance
    ):  # NOTE: might add some looseness to this check later
        return (False, "Main stat value does not match expected value")

    # restore the % sign to the main stat name if it was removed
    if "%" in main_stat_value_str:
        main_stat_value = str(main_stat_value) + "%"
    return True, ""


def get_expected_main_stat_value(
    main_stat_name, main_stats_progression, curLevel, maxLevel, partition
):
    curLevel = int(curLevel)
    maxLevel = int(maxLevel)
    partition = int(partition)

    # if the stat is ATK, HP, or DEF, we need to add the % sign back to the name
    # if it is in partitions 4, 5, or 6 (they have percentage versions of these stats)
    if any(keyword in main_stat_name for keyword in ["ATK", "HP", "DEF"]):
        if partition in [4, 5, 6]:
            main_stat_name += "%"

    # find the base value for this main stat from the progression
    base_value = None
    for stat_name, value in main_stats_progression:
        if stat_name == main_stat_name:
            base_value = value
            break
    if base_value == None:  # check if the main stat name is valid
        return None

    # calculate the range for this stat (base -> 4 * base)
    min_value = base_value
    max_value = base_value * 4

    # calculate what the value should be at the current level
    # the stat progression is split evenly across the levels
    progression_per_level = (max_value - min_value) / (
        maxLevel
    )  # remainder is kept until greater than 1, then added to the value next level
    # as such, the expected value will be rounded down to the nearest whole number
    # floor division will round down
    expected_value_int = (min_value + (progression_per_level * curLevel)) // 1
    expected_value_int = round(expected_value_int)

    # for percentage based stats, the expected value has no rounding
    expected_value_percentage = min_value + (progression_per_level * curLevel)

    if any(keyword in main_stat_name for keyword in percentage_main_stats):
        expected_value = expected_value_percentage
        expected_value = str(expected_value) + "%"  # add the % sign back
    else:
        expected_value = expected_value_int

    return expected_value


# a function to validate the sub stat value of a disk drive within validate_disk_drive
# sub_stats is a list of tuples of the sub stat name and value
def validate_sub_stat_value(sub_stats, sub_stats_progression):
    # convert sub stat values to floats, remove % sign if it is there before converting
    percent_removed_sub_stats = (
        []
    )  # list of tuples of the sub stat name and value where the % sign was removed so we can add it back later
    for i in range(len(sub_stats)):
        sub_stat_name, sub_stat_value = sub_stats[i]
        if "%" in sub_stat_value:
            sub_stat_value = sub_stat_value.split("%")[0]
            percent_removed_sub_stats.append((sub_stat_name, sub_stat_value))
            if any(
                keyword in sub_stat_name for keyword in ["ATK", "HP", "DEF"]
            ):  # these three have % versions
                if "+" in sub_stat_name:
                    # add the % before the + sign back to the name
                    sub_stat_name = (
                        sub_stat_name.split("+")[0] + "%+" + sub_stat_name.split("+")[1]
                    )
                else:
                    sub_stat_name += "%"  # added for the progression comparison
        sub_stats[i] = (sub_stat_name, float(sub_stat_value))

    # first, make sure all sub stats are valid
    for sub_stat_name, sub_stat_value in sub_stats:
        sub_stat_name = sub_stat_name.replace("%", "")  # remove % sign for this check
        # if the sub stat name has a +, cut it off and the characters after it
        if "+" in sub_stat_name:
            sub_stat_name = sub_stat_name.split("+")[0]
        if sub_stat_name not in valid_random_stats:
            return (False, "Invalid sub stat name")

    # NOTE: we don't check the number of expected vs actual rank ups, as disk drives vary in how many substats they come with

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
                        return (False, "Sub stat value should be base value")

    # calculate the total number of rank ups across all ranked up sub stats (eg: if one is +3 and another is +2, the total is 5)
    for sub_stat_name, sub_stat_value in ranked_up_sub_stats:
        rank_up_number = int(sub_stat_name.split("+")[1])
        sub_stat_name = sub_stat_name.split("+")[0]
        # for each ranked up sub stat, check if the value is correct
        # it should be the base value + (rank_up_number * base value)
        base_value = None
        for stat_name, value in sub_stats_progression:
            if stat_name == sub_stat_name:
                base_value = value
                break
        expected_rank_up_value = base_value + (rank_up_number * base_value)
        tolerance = 0.05
        if abs(sub_stat_value - expected_rank_up_value) > tolerance:
            return (False, "Sub stat value does not match expected value")

    # add the percentage sign back to the sub stat names that had it removed and convert them back to strings
    for i in range(len(percent_removed_sub_stats)):
        # find the matching sub stat in sub_stats and add the % sign back
        sub_stat_name, sub_stat_value = percent_removed_sub_stats[i]
        for j in range(len(sub_stats)):
            if sub_stats[j][0].replace("%", "") == sub_stat_name:
                sub_stats[j] = (sub_stat_name, str(sub_stat_value) + "%")

    return (True, "")


# calculate expected sub stat values for a disk drive
# given a list of tuples of the sub stat name and value
# return a list of tuples of the sub stat name and expected value
def get_expected_sub_stat_values(sub_stats, sub_stats_progression):
    # loop through the sub stats and calculate the expected value for each
    # if it is just a unranked sub stat, the expected value is the base value
    # if it is a ranked up sub stat, the expected value is the base value + (rank up number * base value)
    expected_sub_stats = []  # a list of tuples of the sub stat name and expected value
    for sub_stat_name, sub_stat_value in sub_stats:
        if "+" in sub_stat_name:
            rank_up_number = int(sub_stat_name.split("+")[1])
            sub_stat_name = sub_stat_name.split("+")[0]

            # if the sub stat is "ATK", "HP", or "DEF", we need to add the % sign back to the name if its a percentage stat
            if (
                any(keyword in sub_stat_name for keyword in ["ATK", "HP", "DEF"])
                and "%" in sub_stat_value
            ):
                sub_stat_name += "%"

            base_value = None
            for stat_name, value in sub_stats_progression:

                if stat_name == sub_stat_name:
                    base_value = value
                    break
            expected_value = base_value + (rank_up_number * base_value)

            # if the sub stat name is not of the percentage type, we need to round the expected value to the nearest whole number
            if not any(keyword in sub_stat_name for keyword in percentage_sub_stats):
                expected_value = round(expected_value)
            else:
                expected_value = round(expected_value, 1)
                # we don't need to add the % sign back to the value as it is handled in correct_metadata
            sub_stat_name += "+" + str(rank_up_number)
        else:
            # if the sub stat is "ATK", "HP", or "DEF", we need to add the % sign back to the name if its a percentage stat
            if (
                any(keyword in sub_stat_name for keyword in ["ATK", "HP", "DEF"])
                and "%" in sub_stat_value
            ):
                sub_stat_name += "%"
            base_value = None
            for stat_name, value in sub_stats_progression:
                if stat_name == sub_stat_name:
                    base_value = value
                    break
            expected_value = base_value
        expected_sub_stats.append((sub_stat_name, str(expected_value)))
    return expected_sub_stats


# A function to validate the metadata of a disk drive
# main stat is a tuple of the main stat name and value
# sub stats is a list of tuples of the sub stat name and value
def validate_disk_drive(
    set_name, curLevel, maxLevel, partition, main_stat_name, main_stat_value, sub_stats
):
    # convert what we need to ints
    curLevel = int(curLevel)
    maxLevel = int(maxLevel)
    partition = int(partition)

    # check if the set name is valid
    if set_name not in valid_set_names:
        return (False, "Invalid set name")
    rarity = get_rarity_from_maxLevel(maxLevel)
    if rarity == None:  # check if the max level is valid
        return (False, "Invalid max level")
    # check if current level is valid
    if curLevel < 0 or curLevel > maxLevel:
        return (False, "Invalid current level - must be between 0 and max level")

    valid_main_stats = get_partition_main_stats(partition)
    if valid_main_stats == None:  # check if the partition is valid
        return (False, "Invalid partition")
    if main_stat_name not in valid_main_stats:
        return (
            False,
            "Invalid main stat for partition",
        )  # check if the main stat is valid for the partition

    # check if the main stat value is valid
    main_stats_progression, sub_stats_progression = get_rarity_stats(rarity)
    main_stat_value_valid, error = validate_main_stat_value(
        main_stat_name, main_stat_value, main_stats_progression, curLevel, maxLevel
    )
    if not main_stat_value_valid:
        return (False, error)

    # check if the sub stat values are valid
    sub_stats_valid, error = validate_sub_stat_value(sub_stats, sub_stats_progression)
    if not sub_stats_valid:
        return (False, error)

    return (True, "")
