airgrid:
  tagline: "Drone Delivery Network — Air Roads for Urban Logistics"

  delivery_flow:
    steps:
      - store
      - ground_vehicle → nearest_drone_hub
      - drone_hub → air_road → destination_hub
      - lift_down (freight only, separate from residential)
      - ground_vehicle → door

  infrastructure:
    drone_hubs:
      spacing: "every 5km"
      location: "rooftop of tallest building in zone"
      facilities:
        - landing_pads
        - petrol_refueling_stations
        - package_sorting_area
      building_owner_deal: "monthly rent (passive income for them)"

    lift_system:
      type: "dedicated freight elevator"
      rules:
        - separate from residential lift
        - no resident interaction with delivery flow
      ground_floor: "mini locker / handoff zone"

    air_roads:
      altitude: "fixed corridor ~150m"
      lanes: "directional (N→S, E→W)"
      tracking: "real-time GPS visible to customer"

    drones:
      fuel: petrol
      advantages:
        - longer range than battery
        - faster speeds: "80–120 km/h"
        - heavier payloads
        - refuel_time: "minutes (vs 45min battery charge)"

  market_analysis:
    india_logistics_market:
      size: "$6.3B (2024)"
      growth: "~20% YoY"
      hottest_segment: "quick commerce (Blinkit, Zepto, Swiggy Instamart)"

    comparison:
      metric: delivery_time_10km
      ground_delivery: "45–90 min"
      airgrid: "12–18 min"

      metric: traffic_dependency
      ground_delivery: high
      airgrid: zero

      metric: cost_per_delivery
      ground_delivery: "₹40–80"
      airgrid: "₹25–50 (at scale)"

      metric: tracking
      ground_delivery: "vehicle GPS"
      airgrid: "live drone position"

  business_impact:
    for_retailers:
      - same_day → same_hour
      - fewer delivery failures
      - reaches high-rise customers easily

    for_building_owners:
      - passive_rent: "₹50K–5L/month"
      - incentive to onboard fast

    for_customers:
      - real_time_drone_tracking
      - predictable_eta: "no traffic variable"
      - premium_tier: "pay ₹20 extra → deliver in 15 min"

  go_to_market:
    first_b2b_customers:
      - Blinkit
      - Zepto
      - Swiggy Instamart
    reason: "they have stores + inventory + customers, just need the air delivery layer"

  challenges:
    regulatory:
      - "DGCA BVLOS approval needed"
      - "urban petrol drone noise/emission rules"
    operational:
      - "monsoon grounds drones for weeks"
      - "rooftop lease negotiations city-wide"
      - "last-mile ground vehicle still required"

  biggest_opportunity: >
    Plug into quick commerce companies as their delivery layer.
    Replace bike fleets with air network.
    They bring demand, you bring speed.