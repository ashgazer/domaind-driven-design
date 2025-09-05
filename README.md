🛠️ Tactical DDD Patterns (code-level)

These are the ones you already started learning with Python examples.

1. Entity

Object with an identity that stays the same even if attributes change.

Example: a Customer with id.

2. Value Object

No identity, just data + rules.

Interchangeable if values match.

Example: Money(100, "GBP").

3. Aggregate & Aggregate Root

A cluster of entities/value objects that live together and follow consistency rules.

The root is the “gatekeeper” (e.g., Order with OrderItems).

4. Repository

Abstract collection for aggregates.

Lets the domain speak in terms of “find order” without caring about DBs.

Example: OrderRepositoryPort with implementations (in-memory, file, SQL).

5. Factory

Encapsulates complex creation logic.

Example: OrderFactory builds an order with default items.

6. Domain Service

Holds logic that doesn’t naturally belong to a single entity or value object.

Example: DiscountService applying cross-order rules.

7. Modules

Grouping related concepts inside the domain to keep the model organized.

In Python: packages like orders/, payments/.

8. Domain Events (optional, but powerful)

Represent something important that happened in the domain.

Example: OrderSubmitted event could notify other parts of the system.

🗺️ Strategic DDD Patterns (system & team-level)

These are about organizing the big picture.

1. Bounded Context

Defines a boundary where a model applies consistently.

Example: “Orders” context vs “Payments” context. Each can use the word “Invoice” differently without clashing.

2. Context Map

Shows how bounded contexts relate:

Shared Kernel: teams agree on a small shared model.

Customer/Supplier: one context depends on another.

Anti-Corruption Layer: adapter to translate between models.

Conformist: you accept the upstream model “as is”.

3. Ubiquitous Language

Shared vocabulary between developers and domain experts.

Appears in code, tests, and conversations.

Example: if the business says “submit an order”, your method should be order.submit().

4. Subdomains

Break down the problem space:

Core domain: where the company differentiates itself.

Supporting domain: important, but not the core advantage.

Generic domain: commodity stuff (like logging, authentication).

✨ How patterns combine

Imagine our shop system:

Entities: Customer, Order.

Value Objects: Money, Email, ProductId.

Aggregates: Order is root of OrderItems.

Repositories: OrderRepository (port + adapters).

Factories: OrderFactory for clean creation.

Domain Services: DiscountService.

Events: OrderSubmitted event (to trigger shipping).

Bounded Contexts: Orders, Payments, Shipping each have their own models.

Context Map: Orders talks to Payments via an Anti-Corruption Layer.

Ubiquitous Language: Code uses business words directly.


-----
🧑‍💻 How these all fit together
Imagine you’re writing Python for an online shop in memory only:
Entities: Customer, Order


Value Objects: Money, maybe Address


Aggregates: Order as root, with OrderItems


Repository: OrderRepository (keeps Orders in memory)


Service: DiscountService (logic spanning multiple orders)


Factory: OrderFactory (simplify creation)


Bounded Contexts: /orders, /payments, /shipping


Your Domain Model is the sum of all of these.

⚡ So, you’ve got the essentials:
Entities, Value Objects, Aggregates (the “what”).


Repositories, Services, Factories, Bounded Contexts, Ubiquitous Language (the “how” and “where”).

