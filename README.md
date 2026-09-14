Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt build

### Running the containers

This project ships a `docker-compose.yml` with a Postgres database and a dbt container. From the project root:

```bash
# Start the containers in the background
docker-compose up -d

# Run dbt commands inside the dbt container
# (--target docker points dbt at the postgres service instead of localhost)
docker-compose exec dbt dbt build --target docker

# Install dbt package dependencies
docker-compose exec dbt dbt deps

# Run dbt tests
docker-compose exec dbt dbt test --target docker

# Stop the containers
docker-compose down

# Stop the containers and remove the Postgres data volume
docker-compose down -v
```

### Data Tests

dbt's built-in `data_tests` (e.g. `unique`, `not_null`, `accepted_values`) are declared in a model's `.yml` file, under `columns`. Each test compiles to a SQL query that should return **zero rows** — any row returned counts as a failure.

`accepted_values` checks that a column only ever contains values from a fixed list. For example, `models/staging/jaffle_shop/_stg_jaffle_shop.yml` tests the `status` column on `stg_jaffle_shop__orders`:

```yaml
- name: status
  data_tests:
    - accepted_values:
        values: ['placed', 'shipped', 'completed', 'return_pending', 'returned']
```

Two config mistakes to watch for, since dbt's error messages for them look similar but mean different things:

- **Wrong test syntax** — a generic test's arguments (like `values`) must be nested directly under the test name, not wrapped in an extra `arguments:` key. Wrapping them causes `macro 'dbt_macro__test_accepted_values' takes no keyword argument 'arguments'`.
- **Incomplete `values` list** — if the list doesn't cover every value actually present in the column, the test fails on real (valid) rows, not bad data. Run `dbt test` and inspect the compiled SQL under `target/compiled/.../<test_name>.sql`, or query the model directly with `dbt show --inline "select status, count(*) from {{ ref('stg_jaffle_shop__orders') }} group by status"` to see the actual distinct values before deciding whether to fix the list or the data.

In this project, the list was originally missing `return_pending` — a valid order status (a return that hasn't finished processing) present in 2 rows of the source data — so the test failed until it was added to the list.

### Documentation

Documentation is essential for an analytics team to work effectively and efficiently. Strong documentation empowers users to self-service questions about data and enables new team members to on-board quickly.

Documentation often lags behind the code it is meant to describe. This can happen because documentation is a separate process from the coding itself that lives in another tool.

Therefore, documentation should be as automated as possible and happen as close as possible to the coding.

In dbt, models are built in SQL files. These models are documented in YML files that live in the same folder as the models.

**Writing documentation and doc blocks**

Documentation of models occurs in the YML files (where generic tests also live) inside the models directory. It is helpful to store the YML file in the same subfolder as the models you are documenting.

For models, descriptions can happen at the model, source, or column level.

If a longer form, more styled version of text would provide a strong description, doc blocks can be used to render markdown in the generated documentation. For example, `models/staging/jaffle_shop/__jaffle_shop_docs.md` defines an `order_status` doc block with a table explaining each order status value, which is then referenced from `models/staging/jaffle_shop/_stg_jaffle_shop.yml`:

```yaml
- name: status
  description: '{{ doc("order_status") }}'
```

### Deployment

Development in dbt is the process of building, refactoring, and organizing different files in your dbt project. This is done in a development environment using a development schema (`dbt_jsmith`) and typically on a non-default branch (i.e. `feature/customers-model`, `fix/date-spine-issue`). After making the appropriate changes, the development branch is merged to main/master so that those changes can be used in deployment.

Deployment in dbt (or running dbt in production) is the process of running dbt on a schedule in a deployment environment. The deployment environment will typically run from the default branch (i.e., `main`, `master`) and use a dedicated deployment schema (e.g., `dbt_prod`). The models built in deployment are then used to power dashboards, reporting, and other key business decision-making processes.

The use of development environments and branches makes it possible to continue to build your dbt project without affecting the models, tests, and documentation that are running in production.

Curious to know more about deploying with dbt? Check out the free online Advanced Deployment course, where you'll learn how to deploy your dbt project with advanced functionality including continuous integration, orchestrating conflicting jobs, and customizing behavior by environment in the dbt platform!

### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](http://slack.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices
