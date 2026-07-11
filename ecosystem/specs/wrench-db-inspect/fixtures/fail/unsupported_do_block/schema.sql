DO $$
BEGIN
  PERFORM 1;
  PERFORM 'semi;colon';
END;
$$;

CREATE TABLE public.visible_after_do (id bigint PRIMARY KEY);
