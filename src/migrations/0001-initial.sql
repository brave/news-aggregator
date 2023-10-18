create table domain_override_types (
  type text not null primary key
);

insert into domain_override_types (type) values
  ('background_color'),
  ('cover_url')
;

create table domain_overrides (
  domain     text      not null,
  type       text      not null references domain_override_types (type),
  value      text      not null,
  created_at timestamp not null default current_timestamp,
  updated_at timestamp not null default current_timestamp,
  primary key(domain, type)
);