from typing import Any


class Slot:
    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    MELEE = "Melee"
    AMP = "Amp"
    ARCHGUN = "Archgun"
    ARCHGUN_ATMOSPHERE = "Archgun (Atmosphere)"
    ARCHMELEE = "Archmelee"
    EMPLACEMENT = "Emplacement"
    GEAR = "Gear"
    HOUND = "Hound"
    NECH_MELEE = "Nech-Melee"
    RAILJACK_ORDNANCE = "Railjack Ordnance"
    RAILJACK_TURRET = "Railjack Turret"
    ROBOTIC = "Robotic"
    UNIQUE = "Unique"
    VEHICLE = "Vehicle"


class ShotType:
    AOE = "AoE"
    DOT = "DoT"
    HIT_SCAN = "Hit-Scan"
    PROJECTILE = "Projectile"
    THROWN = "Thrown"


class Damage:
    def __init__(self, damage_data: dict[str, float]):
        self.impact = damage_data.get("Impact")
        self.puncture = damage_data.get("Puncture")
        self.slash = damage_data.get("Slash")
        self.heat = damage_data.get("Heat")
        self.cold = damage_data.get("Cold")
        self.electricity = damage_data.get("Electricity")
        self.toxin = damage_data.get("Toxin")
        self.blast = damage_data.get("Blast")
        self.corrosive = damage_data.get("Corrosive")
        self.gas = damage_data.get("Gas")
        self.magnetic = damage_data.get("Magnetic")
        self.radiation = damage_data.get("Radiation")
        self.viral = damage_data.get("Viral")
        self.void = damage_data.get("Void")

    @property
    def used(self) -> dict[str, float]:
        return {key: value for key, value in self.__dict__.items() if value is not None}

    @property
    def total(self) -> float:
        return sum(self.used.values())

    @property
    def most_used(self) -> tuple[str, float]:
        if not self.used:
            raise ValueError("No damage types found")
        damage_type = max(self.used, key=self.used.get)
        percentage = self.used[damage_type] / self.total * 100
        return damage_type, percentage

    def __str__(self) -> str:
        damage_text = "\n".join(
            [f"{key.capitalize()}: {value}" for key, value in self.used.items()]
        )
        most_used_type, most_used_percent = self.most_used
        damage_text += (
            f"\n\nTotal: {round(self.total, 2)} "
            f"({round(most_used_percent, 2)}% {most_used_type.capitalize()})"
        )
        return damage_text


class Attack:
    def __init__(self, attack_data: dict[str, Any]):
        self.attack_name = attack_data.get("AttackName", "Normal Attack")
        self.crit_chance = attack_data.get("CritChance")
        self.crit_multiplier = attack_data.get("CritMultiplier")
        self.damage = Damage(attack_data.get("Damage", {}))
        self.fire_rate = attack_data.get("FireRate")
        self.is_silent = attack_data.get("IsSilent", False)
        self.status_chance = attack_data.get("StatusChance")
        self.multishot = attack_data.get("Multishot")
        self.ammo_cost = attack_data.get("AmmoCost")
        self.punch_through = attack_data.get("PunchThrough")
        self.shot_type = attack_data.get("ShotType")
        self.shot_speed = attack_data.get("ShotSpeed")
        self.max_spread = attack_data.get("MaxSpread")
        self.min_spread = attack_data.get("MinSpread")
        self.accuracy = attack_data.get("Accuracy")
        self.range = attack_data.get("Range")
        self.falloff = attack_data.get("Falloff")
        self.forced_procs = attack_data.get("ForcedProcs", [])
        self.charge_time = attack_data.get("ChargeTime")
        self.trigger = attack_data.get("Trigger")

    def __repr__(self):
        return f"<Attack: {self.attack_name}-{self.shot_type}>"

    @property
    def parsed_falloff(self) -> str | None:
        if self.falloff:
            reduction = self.falloff.get("Reduction")
            if reduction is not None:
                return (
                    f"{round(reduction * 100)}% "
                    f"({self.falloff['StartRange']} - {self.falloff['EndRange']}m)"
                )
        return None

    @property
    def important_properties(self) -> dict[str, Any]:
        props = {}
        props["Crit Chance"] = f"{self.crit_chance * 100}%"
        props["Crit Multiplier"] = f"{self.crit_multiplier}x"
        props["Status Chance"] = f"{round(self.status_chance * 100, 2)}%"

        if self.shot_type != "Normal Attack":
            props["Multishot"] = self.multishot
            props["Fire Rate"] = self.fire_rate

        if self.range:
            label = "AoE Radius" if self.shot_type == "AoE" else "Range"
            props[label] = f"{self.range}m"

        if self.parsed_falloff:
            props["Falloff"] = self.parsed_falloff

        props["**Damage**"] = f"\n{str(self.damage)}"

        return props

    @property
    def title(self) -> str:
        text = f"***Attack Mode***: {self.attack_name}"
        if self.shot_type:
            text += f"\n***Type***: {self.shot_type}"
        return text

    def __str__(self):
        lines = []
        for key, value in self.important_properties.items():
            if value is not None:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


class Weapon:
    def __init__(self, name: str, weapon_data: dict[str, Any]):
        self.name = name
        self.internal_name = weapon_data.get("InternalName")
        self.link = weapon_data.get("Link")
        self.image = weapon_data.get("Image")
        self.slot = weapon_data.get("Slot")
        self.class_ = weapon_data.get("Class")
        self.family = weapon_data.get("Family")
        self.mastery = weapon_data.get("Mastery")
        self.max_rank = weapon_data.get("MaxRank", 30)
        self.disposition = self.parse_disposition(weapon_data.get("Disposition", 0.5))
        self.sell_price = weapon_data.get("SellPrice")
        self.introduced = weapon_data.get("Introduced")
        self.conclave = weapon_data.get("Conclave", False)
        self.traits = weapon_data.get("Traits", [])
        self.polarities = weapon_data.get("Polarities", [])
        self.attacks = [Attack(attack) for attack in weapon_data.get("Attacks", [])]

    def __str__(self) -> str:
        return f"{self.name} ({self.class_})"

    @staticmethod
    def parse_disposition(disposition: float) -> str:
        if disposition >= 1.31:
            return "●●●●●"
        elif disposition >= 1.11:
            return "●●●●○"
        elif disposition >= 0.9:
            return "●●●○○"
        elif disposition >= 0.7:
            return "●●○○○"
        return "●○○○○"

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> "Weapon":
        weapon_slot = data.get("Slot", "")
        if weapon_slot in (Slot.PRIMARY, Slot.SECONDARY):
            return RangedWeapon(name, data)
        elif weapon_slot == Slot.MELEE:
            return MeleeWeapon(name, data)
        else:
            return Weapon(name, data)

    def get_description(self) -> str:
        desc = f"Class: {self.slot}\n"
        desc += f"Type: {self.class_}\n"
        desc += f"Mastery: {self.mastery if self.mastery is not None else '-'}\n"
        desc += f"Disposition: {self.disposition}\n"
        return desc


class RangedWeapon(Weapon):
    def __init__(self, name: str, weapon_data: dict[str, Any]):
        super().__init__(name, weapon_data)
        self.accuracy = weapon_data.get("Accuracy")
        self.ammo_max = weapon_data.get("AmmoMax")
        self.ammo_pickup = weapon_data.get("AmmoPickup")
        self.ammo_type = weapon_data.get("AmmoType")
        self.magazine = weapon_data.get("Magazine")
        self.reload = weapon_data.get("Reload")
        self.trigger = weapon_data.get("Trigger")
        self.exilus_polarity = weapon_data.get("ExilusPolarity")
        self.tradable = weapon_data.get("Tradable")
        self.zoom = weapon_data.get("Zoom")

    def get_description(self) -> str:
        desc = super().get_description()
        desc += f"Ammo: {self.ammo_max if self.ammo_max is not None else '∞'}\n"
        if self.ammo_pickup is not None:
            desc += f"Ammo Pickup: {self.ammo_pickup}\n"
        desc += f"Magazine: {self.magazine}\n"
        desc += f"Reload: {self.reload}\n"
        desc += f"Trigger: {self.trigger}\n"
        if self.zoom:
            desc += "**Zoom**:\n- " + "\n- ".join(str(z) for z in self.zoom) + "\n"
        return desc


class MeleeWeapon(Weapon):
    def __init__(self, name: str, weapon_data: dict[str, Any]):
        super().__init__(name, weapon_data)
        self.block_angle = weapon_data.get("BlockAngle")
        self.combo_dur = weapon_data.get("ComboDur", "∞")
        self.follow_through = weapon_data.get("FollowThrough")
        self.melee_range = weapon_data.get("MeleeRange")
        self.stance_polarity = weapon_data.get("StancePolarity")
        self.sweep_radius = weapon_data.get("SweepRadius")
        self.wind_up = weapon_data.get("WindUp")
        self.attack_speed = self.attacks[0].fire_rate if self.attacks else None
        self.heavy_attack = weapon_data.get("HeavyAttack")
        self.slam_attack = weapon_data.get("SlamAttack")
        self.heavy_slam_attack = weapon_data.get("HeavySlamAttack")
        self.slide_attack = weapon_data.get("SlideAttack")
        self.slam_element = weapon_data.get("SlamElement")
        self.slam_radius = weapon_data.get("SlamRadius")
        self.slam_forced_procs = weapon_data.get("SlamForcedProcs", [])
        self.heavy_slam_element = weapon_data.get("HeavySlamElement")
        self.heavy_slam_radius = weapon_data.get("HeavySlamRadius")
        self.heavy_slam_forced_procs = weapon_data.get("HeavySlamForcedProcs", [])

    def get_description(self) -> str:
        desc = super().get_description()
        if self.block_angle is not None:
            desc += f"Block Angle: {self.block_angle}\n"
        desc += f"Combo Duration: {self.combo_dur}\n"
        desc += f"Follow Through: {self.follow_through}\n"
        desc += f"Attack Speed: {self.attack_speed}\n"
        desc += f"Range: {self.melee_range}m\n"
        return desc
