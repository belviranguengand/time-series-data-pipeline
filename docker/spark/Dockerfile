FROM spark:4.2.0-python3

WORKDIR /opt/project

CMD ["/opt/spark/bin/spark-submit", "--master", "local[*]", "src/spark/aggregate_energy.py"]